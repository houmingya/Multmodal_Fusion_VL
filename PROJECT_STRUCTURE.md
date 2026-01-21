# ====================================
# 项目总览 - 多模态融合Demo
# ====================================

## 📁 完整目录结构

```
multimodal_fusion/
│
├── server/                          # 服务器端（12G显存工作站）
│   ├── app.py                      # ⭐ FastAPI主程序（模型推理）
│   ├── config.py                   # 配置文件
│   ├── requirements.txt            # 依赖清单
│   ├── test_memory.py              # 显存测试脚本
│   ├── start_server.ps1            # Windows启动脚本
│   ├── start_server.sh             # Linux/Mac启动脚本
│   └── image_library/              # 图片库目录
│       ├── README.txt              # 图片库说明
│       ├── cat.jpg                 # 示例图片（需自行添加）
│       ├── dog.jpg                 # 示例图片（需自行添加）
│       └── sunset.jpg              # 示例图片（需自行添加）
│
├── client/                          # 本地端（PC客户端）
│   ├── app.py                      # ⭐ Gradio可视化界面
│   ├── config.py                   # 配置文件
│   ├── requirements.txt            # 依赖清单
│   ├── test_client.py              # 功能测试脚本
│   ├── start_client.ps1            # Windows启动脚本
│   └── start_client.sh             # Linux/Mac启动脚本
│
├── README.md                        # 📖 完整使用文档
├── QUICKSTART.md                    # 🚀 快速开始指南
├── DEPENDENCIES.md                  # 📦 依赖说明文档
├── PROJECT_STRUCTURE.md             # 📁 本文件
└── .gitignore                       # Git忽略规则

```

---

## 📊 文件功能说明

### 核心文件（⭐ 必看）

| 文件 | 大小 | 作用 | 优先级 |
|------|------|------|--------|
| `server/app.py` | ~450行 | FastAPI服务+模型推理 | ⭐⭐⭐ |
| `client/app.py` | ~300行 | Gradio可视化界面 | ⭐⭐⭐ |
| `README.md` | ~500行 | 完整文档 | ⭐⭐⭐ |
| `QUICKSTART.md` | ~200行 | 新手指南 | ⭐⭐ |

### 配置文件

| 文件 | 用途 |
|------|------|
| `server/config.py` | 服务器端参数配置 |
| `client/config.py` | 本地端参数配置 |
| `server/requirements.txt` | 服务器端依赖 |
| `client/requirements.txt` | 本地端依赖 |

### 工具脚本

| 文件 | 用途 |
|------|------|
| `server/test_memory.py` | 验证12G显存适配 |
| `client/test_client.py` | 自动化功能测试 |
| `server/start_server.ps1/.sh` | 一键启动服务器 |
| `client/start_client.ps1/.sh` | 一键启动客户端 |

---

## 🔗 文件依赖关系

```
server/app.py
  ├── 导入: server/config.py (可选)
  ├── 依赖: server/requirements.txt
  └── 数据: server/image_library/

client/app.py
  ├── 导入: client/config.py (可选)
  ├── 依赖: client/requirements.txt
  └── 连接: SERVER_URL (指向server/app.py)
```

---

## 📝 代码行数统计

| 文件 | 行数 | 注释行 | 代码行 | 注释率 |
|------|------|--------|--------|--------|
| `server/app.py` | 450 | 180 | 270 | 40% |
| `client/app.py` | 300 | 100 | 200 | 33% |
| `server/config.py` | 80 | 40 | 40 | 50% |
| `client/config.py` | 60 | 30 | 30 | 50% |
| `test_memory.py` | 100 | 30 | 70 | 30% |
| `test_client.py` | 120 | 30 | 90 | 25% |
| **总计** | **1110** | **410** | **700** | **37%** |

---

## 🎯 核心功能模块

### 服务器端（server/app.py）

```
[启动流程]
1. 加载配置 (config.py)
2. 初始化FastAPI应用
3. 加载LLaVA模型 (load_vqa_model)
4. 加载CLIP模型 (load_clip_model)
5. 构建图片库索引 (build_image_library)
6. 启动Uvicorn服务器

[主要接口]
- GET  /health              # 健康检查
- POST /vqa                 # 图文问答
- POST /text2image_search   # 文搜图

[核心函数]
- load_vqa_model()          # 加载VQA模型（FP16优化）
- load_clip_model()         # 加载CLIP模型
- build_image_library()     # 构建图片索引
- visual_question_answering() # VQA推理
- text_to_image_search()    # 文搜图检索
```

### 本地端（client/app.py）

```
[启动流程]
1. 加载配置 (config.py)
2. 构建Gradio界面 (build_interface)
3. 绑定事件回调
4. 启动Gradio服务器

[主要界面]
- Tab1: 图文问答
  - 图片上传
  - 问题输入
  - 回答展示
- Tab2: 文搜图
  - 文本输入
  - 匹配图片展示

[核心函数]
- check_server_health()     # 连接检查
- vqa_inference()           # VQA请求
- text2image_search()       # 文搜图请求
- build_interface()         # 构建界面
```

---

## 🔄 数据流程图

### 图文问答（VQA）

```
[本地端]              [HTTP]              [服务器端]
用户上传图片   →   编码为JPEG   →   解码为PIL Image
    ↓                                       ↓
输入问题      →   包装为表单   →   LLaVA模型推理
    ↓                                       ↓
点击提交      →   POST请求     →   生成回答文本
    ↓                                       ↓
展示回答      ←   JSON响应     ←   返回结果
```

### 文搜图

```
[本地端]              [HTTP]              [服务器端]
用户输入文本   →   文本字符串   →   CLIP文本编码
    ↓                                       ↓
点击检索      →   POST请求     →   计算余弦相似度
    ↓                                       ↓
展示图片      ←   Base64图片   ←   返回Top-K结果
```

---

## 📦 模型文件存储

### ModelScope自动缓存路径

```
~/.cache/modelscope/
├── hub/
│   ├── damo/
│   │   ├── LLaVA-1.5-7b-v1.1/        # ~14GB
│   │   │   ├── pytorch_model.bin
│   │   │   ├── config.json
│   │   │   └── ...
│   │   └── multi-modal_clip-vit-base-patch16_zh/  # ~1GB
│   │       ├── pytorch_model.bin
│   │       └── ...
```

**总计**：约15GB模型文件（首次下载）

---

## 🧪 测试用例设计

### 单元测试（未来扩展）

```python
# server/tests/test_api.py
def test_health_check()           # 测试健康检查
def test_vqa_inference()          # 测试VQA推理
def test_text2image_search()      # 测试文搜图
def test_empty_image_library()    # 测试空图片库
def test_invalid_image_format()   # 测试无效图片格式
```

### 集成测试

```python
# client/test_client.py (已实现)
- 服务器连接测试
- VQA功能测试
- 文搜图功能测试
```

---

## 🔐 安全性考虑

### 当前实现（开发环境）
- ✅ 输入验证（图片格式、问题长度）
- ✅ 异常捕获（显存不足、网络错误）
- ⚠️ 无认证机制（所有人可访问）
- ⚠️ 无HTTPS加密

### 生产环境建议
- 🔒 启用API Key认证
- 🔒 使用HTTPS加密传输
- 🔒 添加请求频率限制
- 🔒 输入内容过滤（防止恶意提示词）

---

## 📈 性能优化路线图

### 已实现
- ✅ FP16精度（减少50%显存）
- ✅ 模型预加载（避免重复加载）
- ✅ CLIP特征预计算（图片库索引）

### 待优化
- ⏳ INT8量化（进一步减少显存）
- ⏳ 批量推理（多图片并行）
- ⏳ TensorRT加速（推理加速2-5倍）
- ⏳ 模型蒸馏（更小的学生模型）

---

## 🌐 部署场景

### 场景1：本地测试（同一台机器）
```
CLIENT_URL: http://127.0.0.1:7860
SERVER_URL: http://127.0.0.1:8000
```

### 场景2：局域网部署（公司内网）
```
SERVER: 192.168.1.100:8000 (工作站)
CLIENT: 192.168.1.101:7860 (办公电脑)
```

### 场景3：云端部署（公网访问）
```
SERVER: https://api.yourdomain.com (云服务器)
CLIENT: https://demo.yourdomain.com (Web前端)
```

---

## 📚 学习路径建议

### 新手路径
1. 阅读 `QUICKSTART.md` → 5分钟快速部署
2. 运行 `client/test_client.py` → 理解API交互
3. 修改 `client/app.py` → 定制界面样式
4. 阅读 `README.md` → 深入理解原理

### 进阶路径
1. 修改 `server/config.py` → 调整模型参数
2. 运行 `server/test_memory.py` → 优化显存占用
3. 研究 `server/app.py` → 理解模型推理流程
4. 实现新功能 → 如图片相似度搜索

---

## 🛠️ 开发工具推荐

### 必备工具
- **Python IDE**: VS Code / PyCharm
- **API测试**: Postman / curl
- **GPU监控**: nvidia-smi / gpustat

### 推荐插件（VS Code）
- Python (ms-python.python)
- Pylance (代码补全)
- Error Lens (错误高亮)
- GitLens (Git增强)

---

## 📞 技术栈总览

| 层级 | 技术栈 |
|------|--------|
| **前端** | Gradio 4.0+ |
| **后端** | FastAPI 0.104+ |
| **模型** | LLaVA-1.5-7B + CLIP-ViT-B/16 |
| **框架** | PyTorch 2.0+ |
| **模型库** | ModelScope |
| **检索** | Faiss (余弦相似度) |
| **部署** | Uvicorn (ASGI) |

---

## 📝 版本说明

### v1.0.0（当前版本）
- ✅ 图文问答功能（LLaVA）
- ✅ 文搜图功能（CLIP）
- ✅ 12G显存适配
- ✅ Gradio可视化界面
- ✅ 完整文档

### v1.1.0（计划中）
- ⏳ 图片上传管理
- ⏳ 批量问答功能
- ⏳ 历史记录保存
- ⏳ 模型热更新

---

**提示**：本文件为项目结构总览，建议收藏备查。
