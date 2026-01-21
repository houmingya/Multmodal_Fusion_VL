# ====================================
# 本地端启动脚本（Windows PowerShell）
# ====================================

# 激活conda虚拟环境
Write-Host "激活conda虚拟环境..." -ForegroundColor Green
conda activate multimodal_client

# 检查依赖
Write-Host "检查依赖..." -ForegroundColor Green
pip list | Select-String -Pattern "gradio|requests"

# 启动Gradio界面
Write-Host "`n启动Gradio界面..." -ForegroundColor Green
python app.py
