# ====================================
# 模型配置检查脚本
# ====================================
# 用途：检查并验证模型的架构配置
# 功能：下载模型配置，打印模型架构和自动映射信息

import os
from modelscope import snapshot_download  # 从魔搭社区下载模型
from transformers import AutoConfig  # 自动加载模型配置

try:
    # 定义要检查的多模态模型
    model_id = "Qwen/Qwen2.5-VL-3B-Instruct"
    print(f"Checking model {model_id}...")
    
    # 下载模型配置文件到本地缓存目录
    model_dir = snapshot_download(model_id)
    
    # 从本地加载模型配置
    config = AutoConfig.from_pretrained(model_dir, trust_remote_code=True)
    
    # 打印模型架构信息
    print(f"Architectures: {config.architectures}")
    
    # 打印自动模型映射信息（用于自动加载模型）
    print(f"Auto map: {config.auto_map}")
    
except Exception as e:
    # 捕获异常并打印错误信息
    print(f"Error: {e}")
