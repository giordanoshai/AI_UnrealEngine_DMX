# run.py
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
import time
from aetherlight.fixture_config import MOVE_HEAD
from aetherlight.fixture_translator import EffectTranslator

# ============================================================
# 1. 灯具列表（从 UE DMX Library 导出）
# ============================================================
fixtures = [
    {
        "uuid": "AAA", "name": "MH_1", "fixture_id": "4",
        "universe": 0, "address": 1,
        "position": [-3000, 0, 4700],
    },
    {
        "uuid": "BBB", "name": "MH_2", "fixture_id": "4",
        "universe": 0, "address": 9,
        "position": [-1000, 0, 4700],
    },
    {
        "uuid": "CCC", "name": "MH_3", "fixture_id": "4",
        "universe": 0, "address": 17,
        "position": [1000, 0, 4700],
    },
    {
        "uuid": "DDD", "name": "MH_4", "fixture_id": "4",
        "universe": 0, "address": 25,
        "position": [3000, 0, 4700],
    },
]

channel_config = MOVE_HEAD["channels"]

# ============================================================
# 2. 效果 A：自动检测方向（最简写法）
# ============================================================
effect_auto = {
    "effect_name": "auto_wave",
    "primitives": [
        {"channel": "pan",         "animation": "wave",   "params": {"speed": 0.25, "min": 0.2, "max": 0.8, "phase": "auto"}},
        {"channel": "tilt",        "animation": "static", "params": {"value": 0.5}},
        {"channel": "color_wheel", "animation": "static", "params": {"value": "blue"}},
        {"channel": "gobo_wheel",  "animation": "static", "params": {"value": "open"}},
        {"channel": "dimmer",      "animation": "wave",   "params": {"speed": 0.25, "min": 0.3, "max": 1.0, "phase": "auto"}},
        {"channel": "shutter",     "animation": "static", "params": {"value": 0.0}},
        {"channel": "zoom",        "animation": "static", "params": {"value": 0.5}},
        {"channel": "frost",       "animation": "static", "params": {"value": 0.0}},
    ],
}

# ============================================================
# 3. 效果 B：手动指定方向
# ============================================================
effect_manual = {
    "effect_name": "wave_left_to_right",
    "phase_axis": "x",
    "primitives": [
        {"channel": "pan",         "animation": "wave",   "params": {"speed": 0.25, "min": 0.2, "max": 0.8, "phase": "auto"}},
        {"channel": "tilt",        "animation": "static", "params": {"value": 0.5}},
        {"channel": "color_wheel", "animation": "static", "params": {"value": "blue"}},
        {"channel": "gobo_wheel",  "animation": "static", "params": {"value": "open"}},
        {"channel": "dimmer",      "animation": "wave",   "params": {"speed": 0.25, "min": 0.3, "max": 1.0, "phase": "auto"}},
        {"channel": "shutter",     "animation": "static", "params": {"value": 0.0}},
        {"channel": "zoom",        "animation": "static", "params": {"value": 0.5}},
        {"channel": "frost",       "animation": "static", "params": {"value": 0.0}},
    ],
}

# ============================================================
# 4. 运行测试
# ============================================================
translator = EffectTranslator(fixtures, channel_config)

print("=" * 60)
print("【自动检测方向】")
print("=" * 60)
translator.load_effect(effect_auto)

for t in [0.0, 1.0, 2.0]:
    print(f"\n--- t = {t:.1f}s ---")
    frame = translator.to_dmx_frame(t)
    for fixture in translator.sorted_fixtures:
        addr = fixture["address"]
        univ = fixture["universe"]
        dmx = frame[univ][addr]
        print(f"  {fixture['name']:6s}  phase={fixture['phase']:.2f}  "
              f"Pan={dmx[0]:3d}  Dimmer={dmx[5]:3d}")

# ============================================================
# 5. 单灯也行，直接传 [fixture]
# ============================================================
print("\n" + "=" * 60)
print("【单灯测试（自动退化，phase=0.0）】")
print("=" * 60)
single = EffectTranslator([fixtures[0]], channel_config)
single.load_effect(effect_auto)

# ============================================================
# 6. 实时运行 + Art-Net 发送（取消注释启用）
# ============================================================
# from stupidArtnet import StupidArtnet
# artnet = StupidArtnet(target_ip="2.0.0.1", universe=0, packet_size=512)
# artnet.start()
#
# start_time = time.time()
# try:
#     while True:
#         t = time.time() - start_time
#         packets = translator.to_artnet_packets(t)
#         for universe, packet in packets.items():
#             artnet.set(packet)
#         time.sleep(1.0 / 30)  # 30 FPS
# except KeyboardInterrupt:
#     artnet.stop()
#     print("Stopped.")