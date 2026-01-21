# ====================================
# 本地端代码 - Gradio可视化界面（优化版）
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
            return f"✓ 连接正常 | {data['device']} | 图片库: {data['image_library_size']}张"
        else:
            return f"✗ 响应异常 ({response.status_code})"
    except requests.exceptions.ConnectionError:
        return "✗ 无法连接服务器"
    except Exception as e:
        return f"✗ {str(e)}"

def vqa_inference(image, question):
    if image is None:
        return "⚠ 请先上传图片"
    if not question or question.strip() == "":
        return "⚠ 请输入问题"
    
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
            return f"🤖 {result.get('answer', '未返回答案')}"
        else:
            return f"✗ {response.json().get('detail', '未知错误')}"
    except requests.exceptions.Timeout:
        return "✗ 请求超时"
    except requests.exceptions.ConnectionError:
        return "✗ 无法连接服务器"
    except Exception as e:
        return f"✗ {str(e)}"

def text2image_search(text_query, top_k):
    if not text_query or text_query.strip() == "":
        return [], "⚠ 请输入检索文本"
    
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
                return [], "未找到匹配图片"
            
            images = []
            info_text = f"🔍 找到 {len(results)} 张\n\n"
            
            for i, item in enumerate(results, 1):
                if 'image_base64' not in item:
                    return [], f"✗ 缺少image_base64字段"
                img_data = base64.b64decode(item['image_base64'])
                img = Image.open(BytesIO(img_data))
                images.append(img)
                info_text += f"{i}. {item['image']} ({item['score']:.3f})\n"
            
            return images, info_text
        else:
            return [], f"✗ {response.json().get('detail', '未知错误')}"
    except Exception as e:
        return [], f"✗ {str(e)}"

def build_interface():
    custom_css = """
    .gradio-container {
        font-family: "Microsoft YaHei", sans-serif !important;
        max-width: 1400px !important;
    }
    h1 {font-size: 1.6em !important; margin: 8px 0 !important;}
    .gr-button {min-height: 36px !important;}
    .gr-box {padding: 10px !important;}
    """
    
    with gr.Blocks(title="多模态融合Demo") as demo:
        gr.Markdown("# 🚀 多模态融合 Demo")
        
        with gr.Row():
            server_status = gr.Textbox(label="📡 服务器", value="点击检查→", interactive=False, scale=4, max_lines=1)
            check_btn = gr.Button("🔄 检查", size="sm", scale=1)
        check_btn.click(check_server_health, outputs=server_status)
        
        with gr.Tab("📷 图文问答"):
            with gr.Row():
                with gr.Column(scale=1):
                    vqa_image = gr.Image(label="上传图片", type="pil", height=260)
                    vqa_question = gr.Textbox(label="提问", placeholder="图片中有什么？", lines=2)
                    with gr.Row():
                        vqa_clear = gr.ClearButton([vqa_image, vqa_question], value="🗑️", size="sm")
                        vqa_submit = gr.Button("🚀 提交", variant="primary", size="sm", scale=3)
                
                with gr.Column(scale=1):
                    vqa_answer = gr.Textbox(label="回答", lines=11, interactive=False)
            
            with gr.Accordion("💡 示例", open=False):
                gr.Examples([["图片中有什么？"], ["描述这张图片"], ["主要物体是什么？"]], vqa_question)
            
            vqa_submit.click(vqa_inference, [vqa_image, vqa_question], vqa_answer)
        
        with gr.Tab("🔍 文搜图"):
            with gr.Row():
                with gr.Column(scale=1):
                    search_text = gr.Textbox(label="检索", placeholder="一只可爱的猫", lines=2)
                    search_top_k = gr.Slider(label="数量", minimum=1, maximum=10, value=3, step=1)
                    with gr.Row():
                        search_clear = gr.ClearButton([search_text], value="🗑️", size="sm")
                        search_btn = gr.Button("🔍 检索", variant="primary", size="sm", scale=3)
                    search_info = gr.Textbox(label="结果", lines=7, interactive=False)
                
                with gr.Column(scale=2):
                    search_gallery = gr.Gallery(label="匹配图片", columns=3, rows=2, height=380)
            
            with gr.Accordion("💡 示例", open=False):
                gr.Examples([["可爱的猫"], ["日落风景"], ["城市夜景"]], search_text)
            
            search_btn.click(text2image_search, [search_text, search_top_k], [search_gallery, search_info])
        
        with gr.Accordion("📖 说明", open=False):
            gr.Markdown("**问答**: 上传图片→提问→提交 | **搜图**: 输入描述→检索")
    
    return demo

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  多模态融合客户端")
    print("="*50)
    print(f"  服务器: {SERVER_URL}")
    print("="*50 + "\n")
    
    demo = build_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True,
        quiet=True,
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            font-family: "Microsoft YaHei", sans-serif !important;
            max-width: 1400px !important;
        }
        h1 {font-size: 1.6em !important; margin: 8px 0 !important;}
        .gr-button {min-height: 36px !important;}
        .gr-box {padding: 10px !important;}
        """
    )
