# quick_sacn_test.py
"""
快速 sACN 测试 - 发送简单的测试信号到 UE
用于验证网络连接是否正常
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from aetherlight.sacn_sender import SACNSender
import time

def test_basic_connection():
    """基础连接测试 - 发送固定值到所有通道"""
    print("=" * 60)
    print("sACN 基础连接测试")
    print("=" * 60)
    print("\n此测试将发送固定的 DMX 值到 Universe 0")
    print("UE 中应该能看到所有通道都是 128\n")
    
    with SACNSender(source_name="Quick Test") as sender:
        sender.activate_universe(0)
        
        print("正在发送测试数据（10 秒）...")
        print("请在 UE DMX Monitor 中查看 Universe 1\n")
        
        # 发送 10 秒
        test_data = [128] * 512
        for i in range(100):
            sender.send_dmx(0, test_data)
            print(f"\r进度: {i+1}/100", end="", flush=True)
            time.sleep(0.1)
        
        print("\n\n✅ 测试完成！")
        print("\n如果 UE DMX Monitor 中看到数据：")
        print("  ✅ 网络连接正常")
        print("  ✅ sACN 发送成功")
        print("  → 可以运行 test_sacn_ue.py 进行完整测试\n")
        print("如果没有看到数据：")
        print("  ⚠️  检查防火墙设置（UDP 5568）")
        print("  ⚠️  检查 UE DMX Library 配置（Universe 应为 1）")
        print("  ⚠️  确保启用了 'Receive DMX'\n")


def test_moving_light():
    """移动灯光测试 - 循环改变第一个通道的值"""
    print("=" * 60)
    print("sACN 动态灯光测试")
    print("=" * 60)
    print("\n此测试将循环改变 Channel 1 的值（0-255）")
    print("UE 中应该能看到 Pan 通道在移动\n")
    
    with SACNSender(source_name="Moving Test") as sender:
        sender.activate_universe(0)
        
        print("正在发送动态数据（10 秒）...")
        print("请在 UE 中观察灯具的 Pan 轴\n")
        
        start_time = time.time()
        while time.time() - start_time < 10:
            t = time.time() - start_time
            # Pan 通道从 0 到 255 循环
            pan_value = int((t * 50) % 256)
            
            dmx_data = [0] * 512
            dmx_data[0] = pan_value  # Channel 1 = Pan
            dmx_data[4] = 255        # Channel 5 = Dimmer (全亮)
            
            sender.send_dmx(0, dmx_data)
            print(f"\r时间: {t:.1f}s | Pan 值: {pan_value:3d}", end="", flush=True)
            time.sleep(1/30)  # 30 FPS
        
        print("\n\n✅ 测试完成！")
        print("如果看到灯具在移动，说明一切正常！\n")


if __name__ == "__main__":
    print("\n选择测试类型：")
    print("  1. 基础连接测试（所有通道固定值）")
    print("  2. 动态灯光测试（Pan 通道循环）")
    choice = input("\n请输入选择 (1 或 2，默认 1): ").strip()
    
    if choice == "2":
        test_moving_light()
    else:
        test_basic_connection()
