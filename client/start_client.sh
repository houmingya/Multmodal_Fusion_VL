# ====================================
# 本地端启动脚本（Linux/Mac）
# ====================================

#!/bin/bash

# 激活conda虚拟环境
echo "激活conda虚拟环境..."
eval "$(conda shell.bash hook)"
conda activate multimodal_client

# 检查依赖
echo "检查依赖..."
pip list | grep -E "gradio|requests"

# 启动Gradio界面
echo -e "\n启动Gradio界面..."
python app.py
