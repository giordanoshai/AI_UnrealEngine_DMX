# test_sacn_ue.py
"""
测试脚本：通过 sACN 协议发送 DMX 数据到 Unreal Engine
"""
import os
import sys

# 确保可以导入 aetherlight 模块
sys.path.insert(0, os.path.dirname(__file__))

from aetherlight.dmx_translator import run_effect_with_sacn

# 定义效果
effect = {
    "effect_name": "ue_test_effect",
    "description": "UE 测试效果 - 绿色灯光 + Pan/Tilt 扫动",
    "primitives": [
        {"channel": "pan",         "animation": "wave",   "params": {"speed": 0.3, "min": 0.0, "max": 1.0}},
        {"channel": "tilt",        "animation": "wave",   "params": {"speed": 0.2, "min": 0.3, "max": 0.7}},
        {"channel": "color_wheel", "animation": "static", "params": {"value": "green"}},
        {"channel": "gobo_wheel",  "animation": "static", "params": {"value": "open"}},
        {"channel": "dimmer",      "animation": "static", "params": {"value": 1.0}},
        {"channel": "shutter",     "animation": "static", "params": {"value": 1.0}},
        {"channel": "zoom",        "animation": "wave",   "params": {"speed": 0.5, "min": 0.3, "max": 0.9}},
        {"channel": "frost",       "animation": "static", "params": {"value": 0.0}},
    ],
}

# 项目文件路径
project_file = os.path.join(os.path.dirname(__file__), "projects", "TEST1.json")

print("=" * 80)
print("                    sACN → Unreal Engine DMX 测试")
print("=" * 80)
print("\n📡 准备通过 sACN (E1.31) 协议发送 DMX 数据到 UE...")
print("⚠️  请确保：")
print("   1. Unreal Engine 正在运行")
print("   2. UE 中的 DMX 插件已启用并配置为接收 sACN")
print("   3. 网络连接正常（sACN 使用组播地址 239.255.0.x）")
print("\n按 Ctrl+C 可随时停止\n")

# 运行效果（20 秒测试）
run_effect_with_sacn(
    effect_json=effect,
    project_file=project_file,
    fps=30,
    duration=20,
    source_name="AetherLight → UE"
)

print("\n🎉 测试完成！")
print("\n💡 提示：")
print("   - 如果 UE 中的灯没有反应，请检查 DMX Universe 配置")
print("   - 确保 UE DMX Library 中的 Universe 编号与项目文件一致（通常是 0）")
print("   - 可以在 UE 的 DMX Monitor 中查看接收到的数据")
