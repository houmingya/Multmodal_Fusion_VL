# ====================================
# 服务器端启动脚本（Linux/Mac）
# ====================================

#!/bin/bash

# 激活conda虚拟环境
echo "激活conda虚拟环境..."
eval "$(conda shell.bash hook)"
conda activate multimodal_server

# 检查依赖
echo "检查依赖..."
pip list | grep -E "fastapi|torch|modelscope"

# 启动服务器
echo -e "\n启动FastAPI服务器..."
python app.py
