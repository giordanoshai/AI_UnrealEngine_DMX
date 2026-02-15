# demo_cue_player.py
"""
Cue Player 演示脚本
展示如何使用 CuePlayer 播放 cue list
"""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(__file__))

from aetherlight.cue_player import CuePlayer
from aetherlight.sacn_sender import SACNSender
from aetherlight.fixture_config import MOVE_HEAD
from effect_examples import (
    EFFECT_BLUE_WAVE,
    EFFECT_RED_PULSE,
    EFFECT_GREEN_SCAN,
    EFFECT_WHITE_STATIC,
    EFFECT_CIRCLE_ZOOM_GOBO,
)

# 项目文件路径
PROJECT_FILE = os.path.join(os.path.dirname(__file__), "projects", "TEST1.json")


def load_project():
    """加载项目配置"""
    with open(PROJECT_FILE, 'r', encoding='utf-8') as f:
        project_data = json.load(f)
    
    fixtures = project_data.get('fixtures', [])
    channel_config = project_data.get('channel_config', MOVE_HEAD["channels"])
    
    return fixtures, channel_config


def demo_basic_playback():
    """演示基础播放功能"""
    print("=" * 80)
    print("             Cue Player 演示 - 基础播放")
    print("=" * 80)
    
    # 加载项目
    fixtures, channel_config = load_project()
    
    # 初始化 sACN 发送器
    sender = SACNSender()
    universes = set(f.get('universe', 0) for f in fixtures)
    for universe in universes:
        sender.activate_universe(universe)
    
    # 创建 CuePlayer
    player = CuePlayer(sender, fixtures, channel_config, fps=30)
    
    # 创建 Cue List (使用内存中的 effect,不从数据库加载)
    cue_list = {
        "cue_list_name": "演示 Cue List - 基础播放",
        "cues": [
            {
                "cue_number": 1,
                "effect_data": EFFECT_BLUE_WAVE,  # 直接使用 effect 数据
                "transition_type": "CUT",
            },
            {
                "cue_number": 2,
                "effect_data": EFFECT_RED_PULSE,
                "transition_type": "FADE",
                "fade_time": 2.0,
                "ease_type": "ease_in_out_quad",
            },
            {
                "cue_number": 3,
                "effect_data": EFFECT_GREEN_SCAN,
                "transition_type": "FADE",
                "fade_time": 1.5,
                "ease_type": "ease_out_cubic",
            },
            {
                "cue_number": 4,
                "effect_data": EFFECT_WHITE_STATIC,
                "transition_type": "CUT",
            },
        ],
        "loop": False
    }
    
    # 修改 load_cue_list 以支持直接传入 effect_data
    player.load_cue_list(cue_list)
    
    print("\n🎬 开始播放...")
    print("   按 Ctrl+C 可随时停止\n")
    
    # 开始播放
    player.play()
    
    try:
        # 等待播放完成
        while player.is_playing:
            import time
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断播放")
        player.stop()
    
    sender.stop()
    print("\n✅ 演示完成!")


def demo_loop_playback():
    """演示循环播放"""
    print("=" * 80)
    print("             Cue Player 演示 - 循环播放")
    print("=" * 80)
    
    fixtures, channel_config = load_project()
    sender = SACNSender()
    universes = set(f.get('universe', 0) for f in fixtures)
    for universe in universes:
        sender.activate_universe(universe)
    
    player = CuePlayer(sender, fixtures, channel_config, fps=30)
    
    # 创建循环播放的 Cue List
    cue_list = {
        "cue_list_name": "演示 Cue List - 循环播放",
        "cues": [
            {
                "cue_number": 1,
                "effect_data": EFFECT_CIRCLE_ZOOM_GOBO,
                "transition_type": "CUT",
            },
            {
                "cue_number": 2,
                "effect_data": EFFECT_BLUE_WAVE,
                "transition_type": "FADE",
                "fade_time": 3.0,
                "ease_type": "ease_in_out_sine",
            },
        ],
        "loop": True  # 启用循环
    }
    
    player.load_cue_list(cue_list)
    
    print("\n🔁 开始循环播放...")
    print("   将持续播放 30 秒")
    print("   按 Ctrl+C 可随时停止\n")
    
    player.play()
    
    try:
        import time
        time.sleep(30)  # 播放 30 秒
        player.stop()
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断播放")
        player.stop()
    
    sender.stop()
    print("\n✅ 演示完成!")


def demo_manual_control():
    """演示手动控制功能"""
    print("=" * 80)
    print("             Cue Player 演示 - 手动控制")
    print("=" * 80)
    
    fixtures, channel_config = load_project()
    sender = SACNSender()
    universes = set(f.get('universe', 0) for f in fixtures)
    for universe in universes:
        sender.activate_universe(universe)
    
    player = CuePlayer(sender, fixtures, channel_config, fps=30)
    
    cue_list = {
        "cue_list_name": "演示 Cue List - 手动控制",
        "cues": [
            {"cue_number": 1, "effect_data": EFFECT_BLUE_WAVE, "transition_type": "CUT"},
            {"cue_number": 2, "effect_data": EFFECT_RED_PULSE, "transition_type": "FADE", "fade_time": 2.0},
            {"cue_number": 3, "effect_data": EFFECT_GREEN_SCAN, "transition_type": "FADE", "fade_time": 2.0},
            {"cue_number": 4, "effect_data": EFFECT_WHITE_STATIC, "transition_type": "CUT"},
        ],
        "loop": False
    }
    
    player.load_cue_list(cue_list)
    player.play()
    
    print("\n🎮 手动控制模式")
    print("   n - 下一个 Cue")
    print("   p - 上一个 Cue")
    print("   space - 暂停/继续")
    print("   q - 退出")
    print()
    
    try:
        import time
        import msvcrt  # Windows 特定
        
        while player.is_playing:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                
                if key == 'n':
                    player.next_cue()
                elif key == 'p':
                    player.prev_cue()
                elif key == ' ':
                    if player.is_paused:
                        player.resume()
                    else:
                        player.pause()
                elif key == 'q':
                    print("退出...")
                    break
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        player.stop()
        sender.stop()
    
    print("\n✅ 演示完成!")


if __name__ == "__main__":
    print("\n请选择演示模式:")
    print("1. 基础播放 (4个cue,带FADE切换)")
    print("2. 循环播放 (2个cue,循环30秒)")
    print("3. 手动控制 (键盘控制切换)")
    print()
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == "1":
        demo_basic_playback()
    elif choice == "2":
        demo_loop_playback()
    elif choice == "3":
        demo_manual_control()
    else:
        print("❌ 无效选择")
