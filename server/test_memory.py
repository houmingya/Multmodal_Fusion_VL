# ====================================
# 显存测试脚本
# ====================================
# 用途：验证模型加载后的显存占用
# 运行：python test_memory.py

import torch
import sys
from modelscope import Model, AutoTokenizer

print("=" * 60)
print("  显存测试脚本 - 验证12G显存适配")
print("=" * 60)

# 检查GPU
if not torch.cuda.is_available():
    print("✗ 未检测到GPU，无法进行显存测试")
    sys.exit(1)

print(f"\n✓ 检测到GPU: {torch.cuda.get_device_name(0)}")
print(f"  总显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f}GB")

# 清空显存
torch.cuda.empty_cache()
torch.cuda.reset_peak_memory_stats()

print("\n" + "-" * 60)
print("测试1: 加载LLaVA-1.5-7B（FP16优化版）")
print("-" * 60)

try:
    from modelscope import AutoModelForCausalLM
    
    model_id = "damo/LLaVA-1.5-7b-v1.1"
    print(f"正在加载模型: {model_id}")
    
    # FP16精度加载
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )
    
    # 显存统计
    memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
    memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
    peak_memory = torch.cuda.max_memory_allocated(0) / 1024**3
    
    print(f"\n✓ LLaVA模型加载成功")
    print(f"  当前显存占用: {memory_allocated:.2f}GB")
    print(f"  预留显存: {memory_reserved:.2f}GB")
    print(f"  峰值显存: {peak_memory:.2f}GB")
    
    # 判断是否符合要求
    if peak_memory <= 10.0:
        print(f"\n✅ 显存测试通过！（峰值 {peak_memory:.2f}GB ≤ 10GB）")
    else:
        print(f"\n⚠️ 显存超标！（峰值 {peak_memory:.2f}GB > 10GB）")
        print("建议启用INT8量化或使用更小的模型")
    
    # 清理
    del model
    torch.cuda.empty_cache()
    
except Exception as e:
    print(f"\n✗ 加载失败: {str(e)}")
    sys.exit(1)

print("\n" + "-" * 60)
print("测试2: 加载CLIP中文轻量模型")
print("-" * 60)

try:
    model_id = "damo/multi-modal_clip-vit-base-patch16_zh"
    print(f"正在加载模型: {model_id}")
    
    # 重置统计
    torch.cuda.reset_peak_memory_stats()
    
    clip_model = Model.from_pretrained(model_id)
    clip_model.to("cuda")
    
    memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
    peak_memory = torch.cuda.max_memory_allocated(0) / 1024**3
    
    print(f"\n✓ CLIP模型加载成功")
    print(f"  当前显存占用: {memory_allocated:.2f}GB")
    print(f"  峰值显存: {peak_memory:.2f}GB")
    
    del clip_model
    torch.cuda.empty_cache()
    
except Exception as e:
    print(f"\n✗ 加载失败: {str(e)}")

print("\n" + "=" * 60)
print("  测试完成")
print("=" * 60)
