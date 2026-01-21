# ====================================
# 服务器端启动脚本（Windows PowerShell）
# ====================================

# 激活conda虚拟环境
Write-Host "激活conda虚拟环境..." -ForegroundColor Green
conda activate multimodal_server

# 检查依赖
Write-Host "检查依赖..." -ForegroundColor Green
pip list | Select-String -Pattern "fastapi|torch|modelscope"

# 启动服务器
Write-Host "`n启动FastAPI服务器..." -ForegroundColor Green
python app.py
