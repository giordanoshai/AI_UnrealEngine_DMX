# test_multi_fixture.py
"""
测试脚本：将效果发送给 TEST1.json 中的所有灯具
"""
import os
import sys

# 确保可以导入 aetherlight 模块
sys.path.insert(0, os.path.dirname(__file__))

from aetherlight.dmx_translator import run_effect_for_project

# 定义效果
effect = {
    "effect_name": "rainbow_wave",
    "description": "彩虹色波动效果 + Pan/Tilt 扫动",
    "primitives": [
        {"channel": "pan",         "animation": "wave",   "params": {"speed": 0.3, "min": 0.0, "max": 1.0}},
        {"channel": "tilt",        "animation": "wave",   "params": {"speed": 0.2, "min": 0.3, "max": 0.7}},
        {"channel": "color_wheel", "animation": "static", "params": {"value": "green"}},
        {"channel": "gobo_wheel",  "animation": "static", "params": {"value": "open"}},
        {"channel": "dimmer",      "animation": "static", "params": {"value": 1.0}},
        {"channel": "shutter",     "animation": "static", "params": {"value": 0.0}},
        {"channel": "zoom",        "animation": "wave",   "params": {"speed": 0.5, "min": 0.3, "max": 0.9}},
        {"channel": "frost",       "animation": "static", "params": {"value": 0.0}},
    ],
}

# 项目文件路径
project_file = os.path.join(os.path.dirname(__file__), "projects", "TEST1.json")

# 运行效果（15 秒测试）
print("=" * 80)
print("将效果发送给 TEST1.json 中的所有灯具")
print("按 Ctrl+C 可随时停止")
print("=" * 80)

run_effect_for_project(effect, project_file, fps=30, duration=15)

print("\n🎉 测试完成！")
