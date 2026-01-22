# ====================================
# 本地端代码 - Gradio可视化界面（优化版 - Gradio 6.0兼容）
# ====================================
import gradio as gr
import requests
import base64
from io import BytesIO
from PIL import Image
import config

def check_server_health():
    try:
        response = requests.get(f"{config.SERVER_URL}/health", timeout=config.HEALTH_CHECK_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return f"✅ 连接成功 | 设备: {data['device'].upper()} | 图片库: {data['image_library_size']} 张 | 状态: 正常运行"
        else:
            return f"❌ 服务器响应异常 (状态码: {response.status_code})"
    except requests.exceptions.ConnectionError:
        return f"❌ 无法连接到服务器 ({config.SERVER_URL}) - 请确保服务器已启动"
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
            f"{config.SERVER_URL}/vqa",
            files={'image': ('image.jpg', img_byte_arr, 'image/jpeg')},
            data={'question': question.strip()},
            timeout=config.VQA_TIMEOUT
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
        return f"❌ 无法连接到服务器 ({config.SERVER_URL})"
    except Exception as e:
        return f"❌ 发生错误: {str(e)}"

def text2image_search(text_query, top_k):
    if not text_query or text_query.strip() == "":
        return [], "⚠️ 请输入搜索描述"
    
    try:
        response = requests.post(
            f"{config.SERVER_URL}/text2image_search",
            data={'text_query': text_query.strip(), 'top_k': int(top_k)},
            timeout=config.SEARCH_TIMEOUT
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
        return [], f"❌ 无法连接到服务器 ({config.SERVER_URL})"
    except Exception as e:
        return [], f"❌ 发生错误: {str(e)}"

def build_interface():
    with gr.Blocks(title=config.APP_TITLE) as demo:
        gr.Markdown(
            f"""
            # 🚀 {config.APP_TITLE}
            📡 {check_server_health()}
            """
        )
        
        with gr.Tab("📷 图文问答 VQA"):
            with gr.Row():
                with gr.Column(scale=1):
                    vqa_image = gr.Image(
                        label="📤 上传图片", 
                        type="pil", 
                        height=350,
                        sources=["upload", "clipboard"]
                    )
                    vqa_question = gr.Textbox(
                        label="❓ 问题", 
                        placeholder="图片中有什么?", 
                        lines=2
                    )
                    with gr.Row():
                        vqa_submit = gr.Button(
                            "开始分析", 
                            variant="primary", 
                            size="sm", 
                            scale=2
                        )
                        vqa_clear = gr.ClearButton(
                            [vqa_image, vqa_question],
                            value="清空", 
                            size="sm",
                            scale=1
                        )
                
                with gr.Column(scale=1):
                    vqa_answer = gr.Textbox(
                        label="💬 AI 回答", 
                        lines=18, 
                        interactive=False
                    )
            
            gr.Examples(
                examples=[
                    ["图片中有什么?"], 
                    ["描述这张图片"], 
                    ["主要物体是什么?"],
                    ["这是什么场景?"]
                ], 
                inputs=vqa_question,
                label="💡 示例"
            )
            
            vqa_submit.click(vqa_inference, [vqa_image, vqa_question], vqa_answer)
        
        with gr.Tab("🔍 文本搜图"):
            with gr.Row():
                with gr.Column(scale=1):
                    search_text = gr.Textbox(
                        label="🔎 搜索", 
                        placeholder="一只可爱的猫", 
                        lines=2
                    )
                    search_top_k = gr.Slider(
                        label="返回数量", 
                        minimum=1, 
                        maximum=config.MAX_TOP_K, 
                        value=config.DEFAULT_TOP_K, 
                        step=1
                    )
                    with gr.Row():
                        search_btn = gr.Button(
                            "开始检索", 
                            variant="primary", 
                            size="sm", 
                            scale=2
                        )
                        search_clear = gr.ClearButton(
                            [search_text],
                            value="清空", 
                            size="sm",
                            scale=1
                        )
                    search_info = gr.Textbox(
                        label="📋 检索结果", 
                        lines=12, 
                        interactive=False
                    )
                
                with gr.Column(scale=2):
                    search_gallery = gr.Gallery(
                        label="🖼️ 匹配图片", 
                        columns=3, 
                        rows=2, 
                        height=450,
                        object_fit="contain"
                    )
            
            gr.Examples(
                examples=[
                    ["可爱的猫咪"], 
                    ["日落风景"], 
                    ["城市夜景"],
                    ["美丽的花朵"]
                ], 
                inputs=search_text,
                label="💡 示例"
            )
            
            search_btn.click(text2image_search, [search_text, search_top_k], [search_gallery, search_info])
        
        with gr.Accordion("ℹ️ 说明", open=False):
            gr.Markdown(
                """
                **技术栈**: Qwen2.5-VL-3B (4-bit量化) + CLIP 中文版  
                **支持**: 中英文问答 | JPG/PNG/WebP  
                **提示**: 首次推理较慢，请耐心等待
                """
            )
    
    return demo

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🚀 多模态融合客户端 - 启动中")
    print("="*60)
    print(f"  📡 服务器地址: {config.SERVER_URL}")
    print(f"  🌐 本地访问: http://{config.GRADIO_SERVER_NAME}:{config.GRADIO_SERVER_PORT}")
    print("="*60 + "\n")
    
    # 加载CSS样式
    import os
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    with open(css_path, "r", encoding="utf-8") as f:
        custom_css = f.read().replace("{FONT_FAMILY}", config.FONT_FAMILY)
    
    demo = build_interface()
    demo.launch(
        server_name=config.GRADIO_SERVER_NAME,
        server_port=config.GRADIO_SERVER_PORT,
        share=config.GRADIO_SHARE,
        inbrowser=config.GRADIO_INBROWSER,
        quiet=False,
        show_error=True,
        theme=getattr(gr.themes, config.GRADIO_THEME.capitalize())(
            primary_hue="blue",
            secondary_hue="indigo",
            neutral_hue="slate",
            font=["Microsoft YaHei", "SimHei", "sans-serif"]
        ),
        css=custom_css
    )
