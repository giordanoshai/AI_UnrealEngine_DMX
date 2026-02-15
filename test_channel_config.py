# test_channel_config.py
"""测试使用 fixture_config.py 中的通道配置"""
import json
import sys
sys.path.insert(0, '.')

from aetherlight.fixture_translator import EffectTranslator
from aetherlight.fixture_config import MOVE_HEAD

# 加载项目
with open('projects/TEST1.json', 'r', encoding='utf-8') as f:
    project_data = json.load(f)

fixtures = project_data['fixtures'][:1]  # 只测试第一个灯具

# 使用 MOVE_HEAD 配置
channel_config = MOVE_HEAD["channels"]

print("="*60)
print("测试 MOVE_HEAD 通道配置")
print("="*60)

print("\n通道配置（来自 fixture_config.py）:")
for ch_name, ch_conf in channel_config.items():
    print(f"  {ch_name}: offset={ch_conf.get('offset', 'N/A')}, type={ch_conf['type']}")

# 简单效果：dimmer=1.0
effect = {
    "effect_name": "test_dimmer",
    "primitives": [
        {"channel": "pan", "animation": "static", "params": {"value": 0.5}},
        {"channel": "tilt", "animation": "static", "params": {"value": 0.5}},
        {"channel": "dimmer", "animation": "static", "params": {"value": 1.0}},  # 满值
        {"channel": "zoom", "animation": "static", "params": {"value": 0.5}},
        {"channel": "frost", "animation": "static", "params": {"value": 0.0}},
        {"channel": "shutter", "animation": "static", "params": {"value": 1.0}},
        {"channel": "color_wheel", "animation": "static", "params": {"value": "white"}},
        {"channel": "gobo_wheel", "animation": "static", "params": {"value": "open"}},
    ]
}

# 初始化翻译器
translator = EffectTranslator(fixtures, channel_config)
translator.load_effect(effect)

# 获取 DMX 数据
t = 0.0
packets = translator.to_artnet_packets(t)

print("\n生成的 DMX 数据:")
for universe, packet in packets.items():
    print(f"\nUniverse {universe}:")
    # 显示前10个非零通道
    for i in range(10):
        if packet[i] != 0:
            # 根据offset反向查找通道名
            ch_name = "unknown"
            for name, conf in channel_config.items():
                if conf.get("offset") == i:
                    ch_name = name
                    break
            print(f"  DMX[{i+1}] = {packet[i]:3d}  ({ch_name})")

print("\n验证:")
print(f"  DMX[5] (dimmer) = {packets[0][4]} {'✅ 正确' if packets[0][4] == 255 else '❌ 错误'}")
print(f"  根据 MOVE_HEAD 配置，dimmer 的 offset=4，所以在 DMX[5] (index 4)")
