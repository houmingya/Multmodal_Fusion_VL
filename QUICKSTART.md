# ====================================
# 快速开始指南
# ====================================

## 🚀 5分钟快速部署

### 前提条件
- Python 3.10+
- NVIDIA GPU（12GB显存，如RTX 3060/4060Ti/3080）
- 网络连接（首次需下载模型）

---

## 第一步：服务器端部署

### Windows用户

```powershell
# 1. 进入服务器目录
cd server

# 2. 创建conda虚拟环境
conda create -n multimodal_server python=3.10 -y

# 3. 激活虚拟环境
conda activate multimodal_server

# 4. 安装依赖（使用阿里云镜像加速）
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 5. 准备图片库（可选）
# 在 image_library/ 目录放入测试图片

# 6. 启动服务器
python app.py
```

### Linux/Mac用户

```bash
# 1. 进入服务器目录
cd server

# 2. 创建conda虚拟环境
conda create -n multimodal_server python=3.10 -y

# 3. 激活虚拟环境
conda activate multimodal_server

# 4. 安装依赖
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 5. 准备图片库（可选）
# 在 image_library/ 目录放入测试图片

# 6. 启动服务器
python app.py
```

**预期输出**：
```
✓ LLaVA模型加载成功！显存占用: 7.12GB
✓ CLIP模型加载成功！当前总显存占用: 8.23GB
✓ 所有模型加载完成！服务已就绪
```

---

## 第二步：本地端部署

### Windows用户（新开一个PowerShell窗口）

```powershell
# 1. 进入客户端目录
cd client

# 2. 创建conda虚拟环境
conda create -n multimodal_client python=3.10 -y

# 3. 激活虚拟环境
conda activate multimodal_client

# 4. 安装依赖
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 5. 启动Gradio界面
python app.py
```

### Linux/Mac用户（新开一个终端）

```bash
# 1. 进入客户端目录
cd client

# 2. 创建conda虚拟环境
conda create -n multimodal_client python=3.10 -y

# 3. 激活虚拟环境
conda activate multimodal_client

# 4. 安装依赖
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 5. 启动Gradio界面
python app.py
```

**预期结果**：
- 浏览器自动打开 http://127.0.0.1:7860
- 显示Gradio可视化界面

---

## 第三步：功能测试

### 1. 检查连接
- 点击界面顶部"🔄 检查连接"按钮
- 应显示：`✓ 服务器连接正常`

### 2. 测试图文问答
1. 切换到"📷 图文问答"标签页
2. 上传一张图片（如猫的照片）
3. 输入问题："图片中有什么？"
4. 点击"🚀 提交问答"
5. 等待10-30秒查看回答

### 3. 测试文搜图
1. 切换到"🔍 文搜图"标签页
2. 输入："一只可爱的猫"
3. 点击"🔍 开始检索"
4. 查看匹配的图片

---

## ⚙️ 常见配置修改

### 修改服务器地址（局域网/远程访问）

编辑 `client/app.py` 第15行：
```python
SERVER_URL = "http://192.168.1.100:8000"  # 改为服务器实际IP
```

### 修改服务器端口

编辑 `server/app.py` 第18行：
```python
SERVER_PORT = 9000  # 改为其他端口
```

### 添加图片库

```bash
# 进入图片库目录
cd server/image_library

# 复制图片（Windows）
copy C:\Pictures\cat.jpg .

# 复制图片（Linux/Mac）
cp ~/Pictures/cat.jpg .

# 重启服务器以重建索引
```

---

## 🔧 故障排查

### 问题1：服务器启动失败

**错误信息**：`ModuleNotFoundError: No module named 'torch'`

**解决方案**：
```bash
# 确认虚拟环境已激活（命令行前应有括号标记）
# 重新安装依赖
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 问题2：显存不足

**错误信息**：`CUDA out of memory`

**解决方案**：
在 `server/app.py` 第40行启用量化：
```python
# 修改 load_vqa_model() 函数
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(load_in_8bit=True)
vqa_model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=quantization_config,  # 添加此行
    device_map="auto"
)
```

### 问题3：本地无法连接服务器

**检查步骤**：
1. 服务器是否运行：访问 http://localhost:8000/health
2. 防火墙是否开放端口8000
3. SERVER_URL配置是否正确

---

## 📊 性能参考

| 任务 | 首次推理 | 后续推理 | 显存占用 |
|------|---------|---------|---------|
| 图文问答 | 25-30秒 | 5-8秒 | 8.2GB |
| 文搜图 | 2-3秒 | 1-2秒 | 8.5GB |

---

## 📚 下一步

- 查看 [README.md](README.md) 了解详细功能
- 参考 [常见问题](README.md#-常见问题解决) 解决更多问题
- 查看 [配置文件](server/config.py) 进行高级定制

---

**祝使用愉快！** 🎉
