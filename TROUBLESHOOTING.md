# ====================================
# 常见问题排查指南
# ====================================

## 🔍 问题分类索引

1. [环境安装问题](#1-环境安装问题)
2. [模型加载问题](#2-模型加载问题)
3. [显存相关问题](#3-显存相关问题)
4. [网络连接问题](#4-网络连接问题)
5. [功能异常问题](#5-功能异常问题)
6. [性能优化问题](#6-性能优化问题)

---

## 1. 环境安装问题

### Q1.1: pip install失败，提示权限错误

**错误信息**：
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**解决方案**：
```bash
# 方案A：使用虚拟环境（推荐）
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 方案B：用户级安装
pip install --user -r requirements.txt

# 方案C：使用管理员权限（不推荐）
sudo pip install -r requirements.txt
```

---

### Q1.2: PyTorch安装后无法识别GPU

**错误信息**：
```python
>>> torch.cuda.is_available()
False
```

**解决方案**：
```bash
# 1. 检查CUDA版本
nvidia-smi  # 查看Driver Version

# 2. 卸载现有PyTorch
pip uninstall torch torchvision

# 3. 安装匹配的CUDA版本
# CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 4. 验证
python -c "import torch; print(torch.cuda.is_available())"
```

---

### Q1.3: Gradio安装后界面无法打开

**错误信息**：
```
OSError: [Errno 99] Cannot assign requested address
```

**解决方案**：
```python
# 在 client/app.py 中修改
demo.launch(
    server_name="0.0.0.0",  # 改为 "127.0.0.1"
    server_port=7860,
    share=False
)
```

---

## 2. 模型加载问题

### Q2.1: ModelScope模型下载超时

**错误信息**：
```
ConnectionTimeout: HTTPSConnectionPool(host='modelscope.cn', port=443)
```

**解决方案A - 配置镜像源**：
```bash
# Linux/Mac
export MODELSCOPE_CACHE=~/.cache/modelscope
export HF_ENDPOINT=https://hf-mirror.com

# Windows PowerShell
$env:MODELSCOPE_CACHE="$HOME\.cache\modelscope"
```

**解决方案B - 手动下载**：
```bash
# 使用modelscope命令行工具
pip install modelscope[cli]

# 下载模型
modelscope download --model damo/LLaVA-1.5-7b-v1.1 --local_dir ./models/llava

# 修改代码中的模型路径
model_id = "./models/llava"
```

---

### Q2.2: 模型加载卡住不动

**现象**：启动服务器时卡在"正在加载模型..."

**排查步骤**：
```bash
# 1. 检查磁盘空间（至少30GB）
df -h

# 2. 检查网络连接
ping modelscope.cn

# 3. 启用调试模式
export MODELSCOPE_SDK_DEBUG=True
python server/app.py

# 4. 清理缓存重试
rm -rf ~/.cache/modelscope
```

---

### Q2.3: 找不到模型文件

**错误信息**：
```
OSError: damo/LLaVA-1.5-7b-v1.1 does not appear to be a valid model
```

**解决方案**：
```python
# 1. 验证模型ID是否正确
from modelscope import snapshot_download

model_dir = snapshot_download(
    'damo/LLaVA-1.5-7b-v1.1',
    cache_dir='~/.cache/modelscope'
)
print(model_dir)

# 2. 使用完整路径
model_id = "/home/user/.cache/modelscope/hub/damo/LLaVA-1.5-7b-v1.1"
```

---

## 3. 显存相关问题

### Q3.1: CUDA Out of Memory（OOM）

**错误信息**：
```
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB
```

**解决方案A - 启用INT8量化**（推荐）：
```python
# 在 server/app.py 的 load_vqa_model() 中添加
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0
)

vqa_model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=quantization_config,
    device_map="auto"
)
```

**解决方案B - 减少批处理大小**：
```python
# 推理时使用更小的batch size
batch_size = 1  # 默认即为1
```

**解决方案C - 清理显存**：
```python
import torch
torch.cuda.empty_cache()
```

---

### Q3.2: 验证显存占用

**测试脚本**：
```bash
cd server
python test_memory.py
```

**预期输出**：
```
✓ LLaVA模型加载成功
  当前显存占用: 7.12GB
  峰值显存: 7.50GB

✅ 显存测试通过！（峰值 7.50GB ≤ 10GB）
```

**如果超标**：
- 7-10GB：正常，可继续使用
- 10-11GB：启用INT8量化
- >11GB：考虑更小的模型或使用CPU

---

### Q3.3: 推理时显存不断增长

**现象**：多次推理后显存占用越来越高

**解决方案**：
```python
# 在每次推理后添加
with torch.no_grad():
    # 推理代码
    result = model(...)

# 清理缓存
torch.cuda.empty_cache()
gc.collect()
```

---

## 4. 网络连接问题

### Q4.1: 本地无法连接服务器

**错误信息**：
```
Connection refused / No route to host
```

**排查清单**：

**步骤1：验证服务器运行**
```bash
# 在服务器端执行
curl http://localhost:8000/health

# 预期输出
{"status":"healthy","vqa_model_loaded":true,...}
```

**步骤2：检查防火墙**
```bash
# Linux
sudo ufw allow 8000
sudo ufw status

# Windows
# 控制面板 → Windows Defender防火墙 → 高级设置 → 入站规则
# 新建规则 → 端口 → TCP 8000 → 允许连接
```

**步骤3：验证网络连通性**
```bash
# 从本地端测试
ping 服务器IP
telnet 服务器IP 8000

# Windows用户安装telnet
dism /online /Enable-Feature /FeatureName:TelnetClient
```

**步骤4：修改SERVER_URL**
```python
# client/app.py 第15行
SERVER_URL = "http://192.168.1.100:8000"  # 使用实际IP
```

---

### Q4.2: 请求超时

**错误信息**：
```
ReadTimeout: HTTPConnectionPool: Read timed out
```

**解决方案**：
```python
# 在 client/app.py 中增加超时时间
response = requests.post(
    f"{SERVER_URL}/vqa",
    files=files,
    data=data,
    timeout=120  # 改为120秒
)
```

---

### Q4.3: CORS跨域错误

**错误信息**（浏览器控制台）：
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**解决方案**：
```python
# 在 server/app.py 中添加
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 5. 功能异常问题

### Q5.1: 图文问答返回空回答

**现象**：点击提交后返回"抱歉,无法生成回答"

**排查步骤**：

**1. 检查图片格式**
```python
# 支持的格式
valid_formats = ['JPEG', 'PNG', 'WebP', 'BMP']

# 测试图片
from PIL import Image
img = Image.open("test.jpg")
print(img.format)  # 应输出: JPEG
```

**2. 检查问题长度**
```python
# 问题不能为空
if not question or question.strip() == "":
    return "⚠ 请输入问题！"
```

**3. 查看服务器日志**
```bash
# 服务器端会打印详细错误
tail -f server.log
```

---

### Q5.2: 文搜图返回"图片库为空"

**原因**：`server/image_library/` 目录无图片

**解决方案**：
```bash
# 1. 添加测试图片
cd server/image_library
cp ~/Pictures/*.jpg .

# 2. 验证图片格式
ls -lh

# 3. 重启服务器（自动重建索引）
python server/app.py
```

**支持的格式**：jpg, jpeg, png, bmp, webp

---

### Q5.3: Gradio界面中文乱码

**现象**：界面显示方块或问号

**解决方案A - 添加字体**（Linux）：
```bash
# Ubuntu/Debian
sudo apt-get install fonts-noto-cjk

# CentOS/RHEL
sudo yum install google-noto-sans-cjk-fonts

# 重启Gradio
```

**解决方案B - 修改CSS**：
```python
# client/app.py 中修改
custom_css = """
.gradio-container {
    font-family: "Microsoft YaHei", "SimHei", "Arial Unicode MS", sans-serif !important;
}
"""
```

---

### Q5.4: 图片上传失败

**错误信息**：
```
413 Request Entity Too Large
```

**解决方案**：
```python
# 限制图片大小（在 server/app.py 中添加）
from fastapi import File, UploadFile

@app.post("/vqa")
async def vqa(image: UploadFile = File(..., max_length=10*1024*1024)):  # 10MB
    ...
```

---

## 6. 性能优化问题

### Q6.1: 推理速度太慢

**现象**：图文问答需要30秒以上

**优化方案A - 启用编译缓存**：
```python
import torch
torch.backends.cudnn.benchmark = True
torch.backends.cuda.matmul.allow_tf32 = True
```

**优化方案B - 减少生成长度**：
```python
# 在 server/app.py 中修改
result = model.generate(
    **inputs,
    max_new_tokens=256,  # 改为256（默认512）
    temperature=0.7
)
```

**优化方案C - 使用TensorRT**（高级）：
```bash
pip install nvidia-tensorrt
# 需要额外配置，参考TensorRT文档
```

---

### Q6.2: 服务器CPU占用高

**原因**：图片预处理使用CPU

**解决方案**：
```python
# 将预处理移到GPU
image_tensor = preprocess(image).to("cuda")
```

---

### Q6.3: 内存泄漏

**现象**：长时间运行后内存占用增加

**解决方案**：
```python
import gc

# 在推理后添加
del result
gc.collect()
torch.cuda.empty_cache()
```

---

## 📞 获取帮助

### 日志收集
```bash
# 服务器端日志
python server/app.py > server.log 2>&1

# 查看日志
tail -f server.log
```

### 系统信息收集
```bash
# Python版本
python --version

# PyTorch版本
python -c "import torch; print(torch.__version__)"

# GPU信息
nvidia-smi

# 磁盘空间
df -h

# 内存使用
free -h
```

### 提交Issue时请包含
1. 错误信息完整截图
2. 系统信息（上方命令输出）
3. 复现步骤
4. 相关配置文件

---

## 🔗 参考资源

- **ModelScope文档**: https://modelscope.cn/docs
- **FastAPI文档**: https://fastapi.tiangolo.com/
- **Gradio文档**: https://www.gradio.app/docs/
- **PyTorch文档**: https://pytorch.org/docs/

---

**提示**：90%的问题可通过本指南解决，剩余问题请查看README.md或提交Issue。
