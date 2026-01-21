import torch
from PIL import Image
from modelscope import snapshot_download
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    model_id = "Qwen/Qwen2.5-VL-3B-Instruct"
    logger.info("下载模型...")
    model_dir = snapshot_download(model_id)
    
    logger.info("加载处理器...")
    processor = AutoProcessor.from_pretrained(model_dir, trust_remote_code=True)
    
    logger.info("加载模型 (4-bit 量化)...")
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_dir,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    logger.info("创建测试图像...")
    # 创建一个简单的测试图像
    test_image = Image.new('RGB', (224, 224), color='red')
    
    logger.info("准备消息...")
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": test_image},
                {"type": "text", "text": "What color is this image?"},
            ],
        }
    ]
    
    logger.info("应用对话模板...")
    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    logger.info(f"模板文本: {text}")
    
    logger.info("处理视觉信息...")
    image_inputs, video_inputs = process_vision_info(messages)
    logger.info(f"图像输入类型: {type(image_inputs)}, 长度: {len(image_inputs) if image_inputs else 0}")
    
    logger.info("使用处理器处理输入...")
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    
    logger.info(f"输入键: {inputs.keys()}")
    for k, v in inputs.items():
        if isinstance(v, torch.Tensor):
            logger.info(f"  {k}: shape={v.shape}, dtype={v.dtype}, device={v.device}")
    
    logger.info("将输入移到 CUDA...")
    inputs = inputs.to("cuda")
    
    logger.info("开始推理...")
    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=32)
    
    logger.info("解码输出...")
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )[0]
    
    logger.info(f"✓ 推理成功！输出: {output_text}")

except Exception as e:
    logger.error(f"✗ 测试失败: {e}", exc_info=True)
