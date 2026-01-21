# ====================================
# 项目依赖总览
# ====================================

## 📦 依赖包说明

### 服务器端（server/requirements.txt）

| 包名 | 版本 | 用途 | 必需性 |
|------|------|------|--------|
| fastapi | 0.104.1 | Web框架 | 必需 |
| uvicorn | 0.24.0 | ASGI服务器 | 必需 |
| torch | ≥2.0.0 | 深度学习框架 | 必需 |
| torchvision | ≥0.15.0 | 图像处理 | 必需 |
| modelscope | ≥1.11.0 | 模型加载 | 必需 |
| transformers | ≥4.35.0 | 模型推理 | 必需 |
| Pillow | ≥10.0.0 | 图像读取 | 必需 |
| faiss-cpu | ≥1.7.4 | 特征检索 | 必需 |
| numpy | ≥1.24.0 | 数值计算 | 必需 |
| python-multipart | ≥0.0.6 | 文件上传 | 必需 |

**总大小**：约5-8GB（含依赖）

### 本地端（client/requirements.txt）

| 包名 | 版本 | 用途 | 必需性 |
|------|------|------|--------|
| gradio | ≥4.0.0 | 可视化界面 | 必需 |
| requests | ≥2.31.0 | HTTP请求 | 必需 |
| Pillow | ≥10.0.0 | 图像处理 | 必需 |

**总大小**：约500MB（含依赖）

---

## 🔧 安装选项

### 完整安装（推荐）

```bash
# 服务器端
pip install -r server/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 本地端
pip install -r client/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 最小化安装（仅核心依赖）

**服务器端**：
```bash
pip install fastapi uvicorn torch torchvision modelscope transformers Pillow
```

**本地端**：
```bash
pip install gradio requests Pillow
```

---

## 🌐 国内镜像源推荐

### 阿里云（推荐）
```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 清华大学
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 中科大
```bash
pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/
```

---

## ⚡ PyTorch安装（CUDA版本）

### 自动检测（推荐）
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### CUDA 11.8
```bash
pip install torch==2.1.0+cu118 torchvision==0.16.0+cu118 --index-url https://download.pytorch.org/whl/cu118
```

### CUDA 12.1
```bash
pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 --index-url https://download.pytorch.org/whl/cu121
```

### CPU版本（无GPU）
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

---

## 📝 可选依赖

### INT8量化支持（显存不足时）
```bash
pip install bitsandbytes>=0.41.0
```

### TensorRT加速（高级）
```bash
pip install nvidia-tensorrt
```

### 性能监控
```bash
pip install gpustat psutil
```

---

## ✅ 依赖验证

### 验证服务器端
```bash
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"
python -c "from modelscope import Model; print('ModelScope OK')"
```

### 验证本地端
```bash
python -c "import gradio as gr; print('Gradio:', gr.__version__)"
python -c "import requests; print('Requests OK')"
```

---

## 🐛 常见安装问题

### 问题1：PyTorch安装失败

**错误**：`No matching distribution found for torch`

**解决**：
```bash
# 手动指定CUDA版本
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### 问题2：ModelScope下载慢

**解决**：
```bash
# 设置镜像源
export MODELSCOPE_CACHE=~/.cache/modelscope
# 使用魔搭社区加速
```

### 问题3：faiss-cpu安装失败

**解决**：
```bash
# 使用conda安装（更稳定）
conda install -c conda-forge faiss-cpu
```

---

## 📦 虚拟环境管理

### 使用conda（推荐）
```bash
# 服务器端
conda create -n multimodal_server python=3.10 -y
conda activate multimodal_server

# 本地端（新开终端）
conda create -n multimodal_client python=3.10 -y
conda activate multimodal_client
```

### 使用venv（备选）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

---

## 🔄 更新依赖

```bash
# 更新所有包到最新版本
pip install --upgrade -r requirements.txt

# 更新特定包
pip install --upgrade gradio
```

---

## 📊 依赖大小参考

| 环境 | 虚拟环境大小 | 模型缓存 | 总计 |
|------|------------|---------|------|
| 服务器端 | ~8GB | ~15GB | ~23GB |
| 本地端 | ~500MB | 0 | ~500MB |

**建议**：预留30GB磁盘空间（包含模型）

---

**提示**：首次安装可能需要20-40分钟（取决于网络速度）
