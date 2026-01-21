# ====================================
# 本地端代码 - Gradio可视化界面（优化版 - Gradio 6.0兼容）
# ====================================
import gradio as gr
import requests
import base64
from io import BytesIO
from PIL import Image

SERVER_URL = "http://localhost:8000"

def check_server_health():
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"✅ 连接成功 | 设备: {data['device'].upper()} | 图片库: {data['image_library_size']} 张 | 状态: 正常运行"
        else:
            return f"❌ 服务器响应异常 (状态码: {response.status_code})"
    except requests.exceptions.ConnectionError:
        return f"❌ 无法连接到服务器 ({SERVER_URL}) - 请确保服务器已启动"
    except requests.exceptions.Timeout:
        return "⏱️ 连接超时 - 服务器响应过慢"
    except Exception as e:
        return f"❌ 检查失败: {str(e)}"

def vqa_inference(image, question):
    if image is None:
        return "⚠️ 请先上传图片再提问"
    if not question or question.strip() == "":
        return "⚠️ 请输入您的问题"
    
    try:
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        response = requests.post(
            f"{SERVER_URL}/vqa",
            files={'image': ('image.jpg', img_byte_arr, 'image/jpeg')},
            data={'question': question.strip()},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '未返回答案')
            return f"💬 {answer}"
        else:
            error_detail = response.json().get('detail', '未知错误')
            return f"❌ 服务器错误: {error_detail}"
    except requests.exceptions.Timeout:
        return "⏱️ 请求超时,服务器处理时间过长,请稍后重试"
    except requests.exceptions.ConnectionError:
        return f"❌ 无法连接到服务器 ({SERVER_URL})"
    except Exception as e:
        return f"❌ 发生错误: {str(e)}"

def text2image_search(text_query, top_k):
    if not text_query or text_query.strip() == "":
        return [], "⚠️ 请输入搜索描述"
    
    try:
        response = requests.post(
            f"{SERVER_URL}/text2image_search",
            data={'text_query': text_query.strip(), 'top_k': int(top_k)},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            results = result.get('results', [])
            
            if not results:
                return [], "🔍 未找到匹配的图片,请尝试其他搜索词"
            
            images = []
            info_text = f"✅ 成功找到 {len(results)} 张匹配图片\n"
            info_text += f"📝 搜索词: \"{text_query.strip()}\"\n\n"
            info_text += "匹配结果:\n" + "="*40 + "\n"
            
            for i, item in enumerate(results, 1):
                if 'image_base64' not in item:
                    return [], f"❌ 数据格式错误:缺少image_base64字段"
                img_data = base64.b64decode(item['image_base64'])
                img = Image.open(BytesIO(img_data))
                images.append(img)
                score_percentage = item['score'] * 100
                info_text += f"{i}. 📷 {item['image']}\n"
                info_text += f"   相似度: {score_percentage:.1f}%\n\n"
            
            return images, info_text
        else:
            error_detail = response.json().get('detail', '未知错误')
            return [], f"❌ 服务器错误: {error_detail}"
    except requests.exceptions.Timeout:
        return [], "⏱️ 请求超时,请稍后重试"
    except requests.exceptions.ConnectionError:
        return [], f"❌ 无法连接到服务器 ({SERVER_URL})"
    except Exception as e:
        return [], f"❌ 发生错误: {str(e)}"

def build_interface():
    with gr.Blocks(title="多模态融合演示系统") as demo:
        gr.Markdown(
            """
            # 🚀 多模态融合演示系统
            ### 基于 CLIP + BLIP 的视觉语言理解平台
            """
        )
        
        with gr.Row():
            server_status = gr.Textbox(
                label="📡 服务器状态", 
                value="🔄 点击右侧按钮检查连接状态", 
                interactive=False, 
                scale=5,
                max_lines=1
            )
            check_btn = gr.Button("🔄 检查连接", size="sm", scale=1, variant="secondary")
        check_btn.click(check_server_health, outputs=server_status)
        
        with gr.Tab("📷 图文问答 VQA"):
            gr.Markdown("### 上传图片并提出问题,AI 将为您解答")
            with gr.Row():
                with gr.Column(scale=1):
                    vqa_image = gr.Image(
                        label="📤 上传图片", 
                        type="pil", 
                        height=300,
                        sources=["upload", "clipboard"],
                        show_label=True
                    )
                    vqa_question = gr.Textbox(
                        label="❓ 请输入您的问题", 
                        placeholder="例如:图片中有什么?这是什么场景?主要物体是什么?", 
                        lines=3,
                        max_lines=5
                    )
                    with gr.Row():
                        vqa_clear = gr.ClearButton(
                            [vqa_image, vqa_question],
                            value="🗑️ 清空", 
                            size="sm",
                            scale=1
                        )
                        vqa_submit = gr.Button(
                            "🚀 开始分析", 
                            variant="primary", 
                            size="lg", 
                            scale=3
                        )
                
                with gr.Column(scale=1):
                    vqa_answer = gr.Textbox(
                        label="💬 AI 回答", 
                        lines=13, 
                        interactive=False
                    )
            
            with gr.Accordion("💡 示例问题", open=True):
                gr.Examples(
                    examples=[
                        ["图片中有什么?"], 
                        ["描述这张图片的内容"], 
                        ["主要物体是什么颜色?"],
                        ["这是什么场景?"],
                        ["画面中有几个人?"]
                    ], 
                    inputs=vqa_question
                )
            
            vqa_submit.click(vqa_inference, [vqa_image, vqa_question], vqa_answer)
        
        with gr.Tab("🔍 文本搜图 Search"):
            gr.Markdown("### 输入文本描述,从图片库中检索最相关的图片")
            with gr.Row():
                with gr.Column(scale=1):
                    search_text = gr.Textbox(
                        label="🔎 搜索描述", 
                        placeholder="例如:一只可爱的猫、美丽的日落、繁华的城市夜景...", 
                        lines=3,
                        max_lines=5
                    )
                    search_top_k = gr.Slider(
                        label="📊 返回数量", 
                        minimum=1, 
                        maximum=10, 
                        value=5, 
                        step=1,
                        info="选择要返回的图片数量"
                    )
                    with gr.Row():
                        search_clear = gr.ClearButton(
                            [search_text],
                            value="🗑️ 清空", 
                            size="sm",
                            scale=1
                        )
                        search_btn = gr.Button(
                            "🔍 开始检索", 
                            variant="primary", 
                            size="lg", 
                            scale=3
                        )
                    search_info = gr.Textbox(
                        label="📋 检索结果", 
                        lines=9, 
                        interactive=False
                    )
                
                with gr.Column(scale=2):
                    search_gallery = gr.Gallery(
                        label="🖼️ 匹配图片", 
                        columns=3, 
                        rows=3, 
                        height=500,
                        object_fit="contain",
                        show_label=True
                    )
            
            with gr.Accordion("💡 搜索示例", open=True):
                gr.Examples(
                    examples=[
                        ["可爱的猫咪"], 
                        ["壮丽的日落风景"], 
                        ["繁华的城市夜景"],
                        ["美丽的花朵"],
                        ["雪山风光"]
                    ], 
                    inputs=search_text
                )
            
            search_btn.click(text2image_search, [search_text, search_top_k], [search_gallery, search_info])
        
        gr.Markdown("---")
        
        with gr.Accordion("📖 使用说明", open=False):
            gr.Markdown(
                """
                ### 📷 图文问答功能
                1. **上传图片**: 点击上传区域或拖拽图片
                2. **输入问题**: 在文本框中输入您的问题
                3. **获取答案**: 点击「开始分析」按钮,AI 将分析图片并回答
                
                ### 🔍 文本搜图功能
                1. **输入描述**: 在搜索框中输入图片的文本描述
                2. **设置数量**: 调整滑块选择返回图片数量(1-10张)
                3. **开始检索**: 点击「开始检索」按钮查看匹配结果
                
                ### 💡 提示
                - 支持中英文问答和搜索
                - 图片格式支持: JPG、PNG、WebP 等
                - 首次推理可能较慢,请耐心等待
                - 确保服务器已启动并连接正常
                """
            )
        
        with gr.Accordion("⚙️ 技术说明", open=False):
            gr.Markdown(
                """
                - **VQA 模型**: 基于 BLIP/LLaVA 多模态理解模型
                - **检索模型**: CLIP 中文版跨模态检索
                - **架构**: FastAPI 服务端 + Gradio 客户端
                - **GPU 要求**: 推荐 12GB+ 显存
                """
            )
    
    return demo

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🚀 多模态融合客户端 - 启动中")
    print("="*60)
    print(f"  📡 服务器地址: {SERVER_URL}")
    print(f"  🌐 本地访问: http://127.0.0.1:7860")
    print("="*60 + "\n")
    
    demo = build_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True,
        quiet=False,
        show_error=True,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="indigo",
            neutral_hue="slate",
            font=["Microsoft YaHei", "SimHei", "sans-serif"]
        ),
        css="""
        .gradio-container {
            max-width: 1600px !important;
        }
        h1 {
            font-size: 2.2em !important; 
            margin: 16px 0 !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            text-align: center;
        }
        h3 {
            text-align: center;
            color: #666;
            margin-top: -8px;
            margin-bottom: 20px;
        }
        .gr-button {
            min-height: 44px !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
            font-weight: 500 !important;
        }
        .gr-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.15) !important;
        }
        .gr-button-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        .gr-box {
            padding: 18px !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .gr-form {
            border-radius: 12px !important;
        }
        .gr-input, .gr-textarea {
            border-radius: 8px !important;
            border: 1.5px solid #e0e0e0 !important;
        }
        .gr-input:focus, .gr-textarea:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1) !important;
        }
        .tab-nav button {
            font-size: 1.05em !important;
            padding: 14px 24px !important;
            font-weight: 500 !important;
        }
        .tab-nav button.selected {
            background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%) !important;
        }
        label {
            font-weight: 600 !important;
            color: #333 !important;
            margin-bottom: 8px !important;
        }
        """
    )
