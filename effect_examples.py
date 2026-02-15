# effect_examples.py
"""
效果示例播放器 - 从数据库加载效果并演示
"""
import os
import sys
import json
import time

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from aetherlight.fixture_translator import EffectTranslator
from aetherlight.sacn_sender import SACNSender
from aetherlight.database import database
from aetherlight.fixture_config import MOVE_HEAD

# 项目配置文件路径
PROJECT_FILE = os.path.join(current_dir, "projects", "TEST1.json")

def get_available_effects():
    """从数据库获取所有效果"""
    effects_list = database.list_effects()
    # 转换为按序号索引的字典
    effects_map = {}
    for idx, effect in enumerate(effects_list, 1):
        effects_map[str(idx)] = effect
    return effects_map

def run_effect(effect_data: dict, project_file: str, fps: int = 30):
    """
    运行灯光效果
    
    Args:
        effect_data: 效果定义字典
        project_file: 项目配置文件路径
        fps: 帧率 (默认 30)
    """
    # 1. 加载项目配置 (灯具定义)
    if not os.path.exists(project_file):
        print(f"❌ 找不到项目文件: {project_file}")
        return

    try:
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
    except Exception as e:
        print(f"❌ 读取项目文件失败: {e}")
        return
    
    fixtures = project_data.get('fixtures', [])
    if not fixtures:
        print("❌ 项目中未包含任何灯具")
        return

    # 获取通道配置 (默认使用摇头灯配置)
    channel_config = project_data.get('channel_config', MOVE_HEAD["channels"])
    
    # 2. 初始化翻译器
    try:
        translator = EffectTranslator(fixtures, channel_config)
        translator.load_effect(effect_data)
    except Exception as e:
        print(f"❌ 加载效果失败: {e}")
        return
    
    # 3. 初始化 sACN 发送器
    sender = SACNSender()
    universes = set(f.get('universe', 0) for f in fixtures)
    for u in universes:
        sender.activate_universe(u)
    
    # 获取效果信息
    eff_name = effect_data.get('effect_name', 'Unknown')
    eff_desc = effect_data.get('description', 'No description')
    duration = float(effect_data.get('duration', 10.0))
    if duration <= 0:
        duration = 10.0
        
    print(f"\n🎬 正在播放效果: {eff_name}")
    print(f"   描述: {eff_desc}")
    print(f"   时长: {duration} 秒")
    print(f"   FPS: {fps}")
    print(f"   灯具数量: {len(fixtures)}")
    print(f"   Universe: {sorted(list(universes))}")
    print("-" * 60)
    
    frame_time = 1.0 / fps
    total_frames = int(duration * fps)
    
    try:
        for frame in range(total_frames):
            t = frame / fps
            
            # 计算当前帧的 DMX 数据
            packets = translator.to_artnet_packets(t)
            
            # 发送数据
            for universe, dmx_data in packets.items():
                sender.send_dmx(universe, dmx_data)
            
            # 打印进度
            if frame % fps == 0:
                progress = (frame / total_frames) * 100
                print(f"⏱️  {t:.1f}s / {duration}s ({progress:.0f}%)", end='\r')
            
            # 保持帧率
            time.sleep(frame_time)
            
        print(f"\n✅ 播放结束 ({duration}s)")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断播放")
    except Exception as e:
        print(f"\n❌ 播放过程中出错: {e}")
    finally:
        sender.stop()
        print("DMX 发送已停止")


if __name__ == "__main__":
    print("=" * 60)
    print("               灯光效果演示播放器")
    print("=" * 60)
    
    # 检查数据库中的效果
    effects = get_available_effects()
    
    if not effects:
        print("❌ 数据库中没有找到效果 (data/effects.json 数据为空)")
        print("   请先运行 import_effects.py 或在主程序中创建效果。")
        sys.exit(1)
        
    print(f"\n可用效果列表:")
    for key, eff in effects.items():
        name = eff.get('effect_name', 'Unnamed')
        desc = eff.get('description', '')
        print(f"  {key}. {name:<20} - {desc}")
        
    print(f"\n请选择效果编号 (1-{len(effects)}) 或直接回车选择第一个:")
    choice = input("> ").strip()
    
    if not choice:
        choice = "1"
        
    if choice not in effects:
        print(f"❌ 无效选择: {choice}")
        sys.exit(1)
        
    selected_effect = effects[choice]
    
    # 运行选中效果
    run_effect(selected_effect, PROJECT_FILE)



