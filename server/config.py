# ====================================
# 服务器配置文件
# ====================================

import torch

# ====================================
# 服务器配置
# ====================================
SERVER_HOST = "0.0.0.0"  # 服务器监听地址
SERVER_PORT = 8000       # 服务器端口

# ====================================
# 路径配置
# ====================================
IMAGE_LIBRARY_PATH = "./image_library"  # 图片库路径

# ====================================
# 设备配置
# ====================================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ====================================
# 模型配置
# ====================================
# VQA 模型配置
VQA_MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"

# VQA 量化配置
VQA_QUANTIZATION_CONFIG = {
    "load_in_4bit": True,
    "bnb_4bit_quant_type": "nf4",
    "bnb_4bit_compute_dtype": torch.float16,
    "bnb_4bit_use_double_quant": True,  # 双量化进一步节省显存
}

# VQA 推理参数
VQA_GENERATION_CONFIG = {
    "max_new_tokens": 128,  # 减少生成长度以节省显存
    "do_sample": False,     # 使用贪心解码而非采样
    "num_beams": 1,         # 不使用束搜索
}

# CLIP 模型配置
CLIP_MODEL_ID = "iic/multi-modal_clip-vit-base-patch16_zh"

# CLIP 图像预处理配置
CLIP_IMAGE_SIZE = (224, 224)
CLIP_NORMALIZE_MEAN = [0.48145466, 0.4578275, 0.40821073]  # 图像归一化均值 (RGB通道)
CLIP_NORMALIZE_STD = [0.26862954, 0.26130258, 0.27577711]  # 图像归一化标准差 (RGB通道)

# ====================================
# 图片库配置
# ====================================
VALID_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

# ====================================
# 日志配置
# ====================================
LOG_LEVEL = "INFO"
