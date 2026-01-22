# ====================================
# 服务器端代码 - FastAPI服务
# ====================================
# 功能：提供VQA图文问答和文搜图接口
# 模型：Qwen2.5-VL-3B-Instruct (VQA) + CLIP (Search)
# 环境：12G显存工作站 + Python 3.10+

import os
import io
import gc
import torch
import numpy as np
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import logging
import ssl
import certifi

# 禁用SSL证书验证（解决ModelScope下载问题）
ssl._create_default_https_context = ssl._create_unverified_context

from modelscope import snapshot_download
# 直接导入 Qwen2.5 VL 的特定类
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info
import config

# 配置日志
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# 创建图片库目录
os.makedirs(config.IMAGE_LIBRARY_PATH, exist_ok=True)

# ====================================
# 全局变量
# ====================================
app = FastAPI(title="多模态融合服务", description="VQA图文问答 (Qwen2.5-VL-3B) + 文搜图服务")

vqa_model = None
vqa_processor = None
clip_model = None
clip_preprocessor = None
clip_tokenizer = None
image_library = {}

def load_vqa_model(): # VQA 是 Visual Question Answering（视觉问答）的缩写
    """
    加载 Qwen2.5-VL-3B-Instruct 模型
    """
    global vqa_model, vqa_processor
    try:
        model_id = config.VQA_MODEL_ID
        logger.info(f"正在加载 VQA 模型: {model_id} ...")

        # 1. 优先使用配置的本地路径，否则尝试自动查找缓存，最后才下载
        if config.VQA_LOCAL_MODEL_PATH and os.path.exists(config.VQA_LOCAL_MODEL_PATH):
            logger.info(f"使用配置的本地模型: {config.VQA_LOCAL_MODEL_PATH}")
            model_dir = config.VQA_LOCAL_MODEL_PATH
        else:
            # 尝试查找 ModelScope 缓存
            cache_dir = os.path.expanduser("~/.cache/modelscope/hub")
            # ModelScope 可能使用多种命名方式
            possible_paths = [
                os.path.join(cache_dir, model_id.replace("/", "---")),
                os.path.join(cache_dir, model_id.replace("/", "/")),
                os.path.join(cache_dir, model_id),
            ]
            
            model_dir = None
            for path in possible_paths:
                if os.path.exists(path):
                    logger.info(f"找到本地缓存模型: {path}")
                    model_dir = path
                    break
            
            if not model_dir:
                logger.info(f"本地模型不存在，开始下载...")
                logger.info(f"提示：如已下载，请在 config.py 中设置 VQA_LOCAL_MODEL_PATH")
                model_dir = snapshot_download(model_id)

        # 2. 加载模型
        # 使用 Qwen2_5_VLForConditionalGeneration 类
        # 启用 4-bit 量化以节省显存 (12GB 显存下推荐)
        quantization_config = BitsAndBytesConfig(**config.VQA_QUANTIZATION_CONFIG)
        
        try:
            logger.info("正在尝试以 4-bit 量化加载模型 (BitsAndBytes)...")
            vqa_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_dir,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True,  # 降低 CPU 内存使用
            )
            # 设置为评估模式
            vqa_model.eval()
        except Exception as e:
            logger.error(f"加载 Qwen2_5_VLForConditionalGeneration 失败: {e}")
            raise e

        # 3. 加载处理器
        vqa_processor = AutoProcessor.from_pretrained(model_dir, trust_remote_code=True)

        if torch.cuda.is_available():
            mem_use = torch.cuda.memory_allocated(0) / 1024**3
            mem_reserved = torch.cuda.memory_reserved(0) / 1024**3
            logger.info(f"✓ VQA 模型加载成功！")
            logger.info(f"  显存使用: {mem_use:.2f}GB / 保留: {mem_reserved:.2f}GB")

    except Exception as e:
        logger.error(f"✗ VQA 模型加载失败: {str(e)}")
        raise

def load_clip_model():
    """
    加载 CLIP 图文检索模型 (保持不变)
    """
    global clip_model, clip_preprocessor, clip_tokenizer
    try:
        logger.info("正在加载 CLIP 中文轻量模型...")
        from modelscope import Model, AutoTokenizer

        model_id = config.CLIP_MODEL_ID
        
        # 优先使用配置的本地路径
        if config.CLIP_LOCAL_MODEL_PATH and os.path.exists(config.CLIP_LOCAL_MODEL_PATH):
            logger.info(f"使用配置的本地模型: {config.CLIP_LOCAL_MODEL_PATH}")
            model_dir = config.CLIP_LOCAL_MODEL_PATH
        else:
            # 尝试查找 ModelScope 缓存
            cache_dir = os.path.expanduser("~/.cache/modelscope/hub")
            possible_paths = [
                os.path.join(cache_dir, model_id.replace("/", "---")),
                os.path.join(cache_dir, model_id.replace("/", "/")),
                os.path.join(cache_dir, model_id),
            ]
            
            model_dir = None
            for path in possible_paths:
                if os.path.exists(path):
                    logger.info(f"找到本地缓存模型: {path}")
                    model_dir = path
                    break
            
            if not model_dir:
                logger.info(f"本地模型不存在，开始下载...")
                logger.info(f"提示：如已下载，请在 config.py 中设置 CLIP_LOCAL_MODEL_PATH")
                model_dir = model_id  # 让 ModelScope 自动下载
        
        clip_model = Model.from_pretrained(model_dir)
        clip_model.to(config.DEVICE)
        clip_model.eval()

        # tokenizer 使用相同的路径
        clip_tokenizer = AutoTokenizer.from_pretrained(model_dir if model_dir != model_id else model_id)

        from torchvision import transforms
        clip_preprocessor = transforms.Compose([
            transforms.Resize(config.CLIP_IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=config.CLIP_NORMALIZE_MEAN,
                std=config.CLIP_NORMALIZE_STD
            )
        ])

        if torch.cuda.is_available():
            mem_use = torch.cuda.memory_allocated(0) / 1024**3
            mem_reserved = torch.cuda.memory_reserved(0) / 1024**3
            logger.info(f"✓ CLIP 模型加载成功！")
            logger.info(f"  显存使用: {mem_use:.2f}GB / 保留: {mem_reserved:.2f}GB")

    except Exception as e:
        logger.error(f"✗ CLIP 模型加载失败: {str(e)}")
        raise

def build_image_library():
    """构建图片库索引"""
    global image_library
    try:
        logger.info(f"构建图片库索引: {config.IMAGE_LIBRARY_PATH} ...")
        valid_extensions = config.VALID_IMAGE_EXTENSIONS
        
        if not os.path.exists(config.IMAGE_LIBRARY_PATH):
            logger.warning(f"⚠ 图片库目录不存在: {config.IMAGE_LIBRARY_PATH}")
            return
            
        image_files = [f for f in os.listdir(config.IMAGE_LIBRARY_PATH) 
                      if os.path.splitext(f.lower())[1] in valid_extensions]

        if not image_files:
            logger.warning("⚠ 图片库为空")
            return

        for img_file in image_files:
            img_path = os.path.join(config.IMAGE_LIBRARY_PATH, img_file)
            try:
                image = Image.open(img_path).convert("RGB")
                image_tensor = clip_preprocessor(image).unsqueeze(0).to(config.DEVICE)
                
                with torch.no_grad():
                    # 使用 ModelScope CLIP 的 encode_image 方法
                    image_features = clip_model.clip_model.encode_image(image_tensor)
                    # 归一化
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                
                image_library[img_file] = image_features.cpu().numpy()
            except Exception as e:
                logger.warning(f"处理图片 {img_file} 失败: {e}")

        logger.info(f"✓ 图片库构建完成，共 {len(image_library)} 张")

    except Exception as e:
        logger.error(f"✗ 图片库构建失败: {str(e)}")

@app.on_event("startup")
async def startup_event():
    logger.info("系统初始化启动...")
    load_vqa_model()
    load_clip_model()
    build_image_library()
    logger.info("✓ 服务启动完成")

@app.post("/vqa")
async def visual_question_answering(
    image: UploadFile = File(...),
    question: str = Form(...)
):
    try:
        # 清理显存缓存
        torch.cuda.empty_cache()
        
        # 1. 读取图片
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        logger.info(f"VQA Request: {question}")

        # 2. 构建 Qwen2.5-VL 消息格式
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": pil_image},
                    {"type": "text", "text": question},
                ],
            }
        ]

        # 3. 预处理
        text = vqa_processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        image_inputs, video_inputs = process_vision_info(messages)

        inputs = vqa_processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(config.DEVICE)

        # 4. 推理 - 使用更保守的参数
        with torch.no_grad():
            generated_ids = vqa_model.generate(
                **inputs, 
                **config.VQA_GENERATION_CONFIG
            )

        # 5. 解码 (去掉输入的 token)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = vqa_processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]

        logger.info(f"VQA Answer: {output_text}")
        
        # 清理显存
        del inputs, generated_ids, generated_ids_trimmed
        torch.cuda.empty_cache()

        return JSONResponse({"status": "success", "question": question, "answer": output_text})

    except Exception as e:
        logger.error(f"VQA Error: {str(e)}")
        # 清理显存
        torch.cuda.empty_cache()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text2image_search")
async def text_to_image_search(text_query: str = Form(...), top_k: int = Form(5)):
    """文本搜索图片 - 接受 text_query 参数以匹配客户端"""
    try:
        if not image_library:
            raise HTTPException(status_code=400, detail="图片库为空")

        logger.info(f"Search Request: {text_query}, top_k={top_k}")

        # 文本编码 - 使用 ModelScope CLIP 的 encode_text 方法
        text_tokens = clip_tokenizer(text_query, return_tensors="pt", padding=True, truncation=True)
        # 将 input_ids 移到 GPU (encode_text 只需要 input_ids)
        input_ids = text_tokens['input_ids'].to(config.DEVICE)

        with torch.no_grad():
            text_features = clip_model.clip_model.encode_text(input_ids)
            # 归一化
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        text_features_np = text_features.cpu().numpy()

        # 计算相似度
        similarities = {}
        for img_file, img_features in image_library.items():
            similarity = np.dot(text_features_np[0], img_features[0])
            similarities[img_file] = float(similarity)

        # 排序并取 top_k
        top_results = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]

        logger.info(f"Search Results: {len(top_results)} images found")
        import base64

        def image_to_base64(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')

        return JSONResponse({
            "status": "success",
            "query": text_query,
            "results": [
                    {
                        "image": img,
                        "score": score,
                        "image_base64": image_to_base64(os.path.join(config.IMAGE_LIBRARY_PATH, img))
                    }
                    for img, score in top_results
                ]
        })

    except Exception as e:
        logger.error(f"Search Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """检查服务状态"""
    health_info = {
        "status": "healthy",
        "vqa_model_loaded": vqa_model is not None,
        "clip_model_loaded": clip_model is not None,
        "image_library_size": len(image_library),
        "device": config.DEVICE
    }
    
    if torch.cuda.is_available():
        health_info["gpu_memory_allocated_gb"] = round(torch.cuda.memory_allocated(0) / 1024**3, 2)
        health_info["gpu_memory_reserved_gb"] = round(torch.cuda.memory_reserved(0) / 1024**3, 2)
    
    return health_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.SERVER_HOST, port=config.SERVER_PORT)
