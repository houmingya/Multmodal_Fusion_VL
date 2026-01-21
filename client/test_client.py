# ====================================
# 完整测试脚本 - 本地端
# ====================================
# 用途：自动化测试所有功能
# 运行：python test_client.py

import requests
import sys
from pathlib import Path

# 配置
SERVER_URL = "http://localhost:8000"

print("=" * 60)
print("  多模态融合客户端测试")
print("=" * 60)

# ====================================
# 测试1：健康检查
# ====================================
print("\n测试1: 服务器连接")
print("-" * 60)

try:
    response = requests.get(f"{SERVER_URL}/health", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 服务器连接成功")
        print(f"  - VQA模型: {'已加载' if data['vqa_model_loaded'] else '未加载'}")
        print(f"  - CLIP模型: {'已加载' if data['clip_model_loaded'] else '未加载'}")
        print(f"  - 图片库: {data['image_library_size']}张")
        print(f"  - 设备: {data['device']}")
    else:
        print(f"✗ 服务器响应异常: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"✗ 连接失败: {str(e)}")
    print("\n请检查：")
    print("1. 服务器是否已启动（运行 server/app.py）")
    print("2. SERVER_URL 配置是否正确")
    print("3. 防火墙是否开放端口")
    sys.exit(1)

# ====================================
# 测试2：图文问答（需要手动准备测试图片）
# ====================================
print("\n测试2: 图文问答（VQA）")
print("-" * 60)

# 检查是否有测试图片
test_image_path = Path("test_image.jpg")
if not test_image_path.exists():
    print("⚠️ 未找到测试图片 test_image.jpg")
    print("   请准备一张测试图片并命名为 test_image.jpg")
    print("   跳过VQA测试...")
else:
    try:
        with open(test_image_path, "rb") as f:
            files = {"image": ("test.jpg", f, "image/jpeg")}
            data = {"question": "图片中有什么？"}
            
            print("发送VQA请求...")
            response = requests.post(
                f"{SERVER_URL}/vqa",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ VQA推理成功")
                print(f"  问题: {result['question']}")
                print(f"  回答: {result['answer']}")
            else:
                print(f"✗ VQA推理失败: {response.json().get('detail', '未知错误')}")
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")

# ====================================
# 测试3：文搜图
# ====================================
print("\n测试3: 文搜图")
print("-" * 60)

try:
    data = {
        "text_query": "一只可爱的猫",
        "top_k": 3
    }
    
    print("发送文搜图请求...")
    response = requests.post(
        f"{SERVER_URL}/text2image_search",
        data=data,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        results = result.get('results', [])
        
        if results:
            print(f"✓ 文搜图成功（共{len(results)}张）")
            for i, item in enumerate(results, 1):
                print(f"  {i}. {item['image_name']} (相似度: {item['similarity_score']:.4f})")
        else:
            print("⚠️ 未找到匹配图片（图片库可能为空）")
    elif response.status_code == 404:
        print("⚠️ 服务器图片库为空")
        print("   请在 server/image_library/ 目录添加图片后重启服务器")
    else:
        print(f"✗ 文搜图失败: {response.json().get('detail', '未知错误')}")
except Exception as e:
    print(f"✗ 测试失败: {str(e)}")

# ====================================
# 总结
# ====================================
print("\n" + "=" * 60)
print("  测试完成")
print("=" * 60)
print("\n如果所有测试通过，可以启动Gradio界面进行交互测试。")
print("运行命令: python client/app.py")
