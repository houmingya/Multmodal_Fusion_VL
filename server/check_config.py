import os
from modelscope import snapshot_download
from transformers import AutoConfig

try:
    model_id = "Qwen/Qwen2.5-VL-3B-Instruct"
    print(f"Checking model {model_id}...")
    model_dir = snapshot_download(model_id)
    
    config = AutoConfig.from_pretrained(model_dir, trust_remote_code=True)
    print(f"Architectures: {config.architectures}")
    print(f"Auto map: {config.auto_map}")
    
except Exception as e:
    print(f"Error: {e}")
