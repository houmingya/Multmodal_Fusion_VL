# ====================================
# 配置文件 - 服务器端
# ====================================
# 用途：集中管理服务器配置参数
# 使用：在 app.py 中导入此文件

import os

# ====================================
# 基础服务配置
# ====================================
SERVER_HOST = "0.0.0.0"  # 监听地址（0.0.0.0允许外部访问，127.0.0.1仅本地）
SERVER_PORT = 8000       # 服务端口

# ====================================
# 模型配置
# ====================================
# LLaVA图文问答模型
VQA_MODEL_ID = "damo/LLaVA-1.5-7b-v1.1"
VQA_DEVICE = "cuda"      # 计算设备：cuda 或 cpu
VQA_DTYPE = "float16"    # 精度：float16 或 float32（FP16减少50%显存）

# CLIP图文检索模型
CLIP_MODEL_ID = "damo/multi-modal_clip-vit-base-patch16_zh"
CLIP_DEVICE = "cuda"

# ====================================
# 图片库配置
# ====================================
IMAGE_LIBRARY_PATH = "./image_library"  # 图片库目录路径
VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}  # 支持的图片格式

# ====================================
# 推理配置
# ====================================
VQA_MAX_NEW_TOKENS = 512     # VQA最大生成token数
VQA_TEMPERATURE = 0.7        # 生成温度（0.1-1.0，越低越确定）
VQA_TOP_P = 0.9              # 核采样参数

CLIP_IMAGE_SIZE = 224        # CLIP输入图片尺寸
CLIP_MAX_TEXT_LENGTH = 77    # CLIP最大文本长度

# ====================================
# 性能优化配置
# ====================================
ENABLE_INT8_QUANTIZATION = False  # 是否启用INT8量化（显存不足时开启）
LOW_CPU_MEM_USAGE = True         # 低CPU内存模式
DEVICE_MAP_AUTO = True           # 自动设备分配

# ====================================
# 日志配置
# ====================================
LOG_LEVEL = "INFO"  # 日志级别：DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ====================================
# 安全配置（生产环境使用）
# ====================================
ENABLE_API_KEY = False       # 是否启用API Key验证
API_KEY = "your-secret-key"  # API密钥（如启用验证）
ENABLE_CORS = True           # 是否允许跨域请求
ALLOWED_ORIGINS = ["*"]      # 允许的来源（生产环境改为具体域名）

# ====================================
# 魔搭社区配置
# ====================================
MODELSCOPE_CACHE = os.path.expanduser("~/.cache/modelscope")  # 模型缓存路径
os.environ["MODELSCOPE_CACHE"] = MODELSCOPE_CACHE
