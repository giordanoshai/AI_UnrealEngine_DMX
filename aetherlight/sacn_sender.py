# sacn_sender.py
"""
sACN (Streaming ACN / E1.31) 发送器
用于通过网络发送 DMX 数据到 Unreal Engine 等应用
"""
import sacn
import time
from typing import Dict, List


class SACNSender:
    """sACN DMX 数据发送器"""
    
    def __init__(self, source_name: str = "AetherLight DMX", universe_offset: int = 1):
        """
        初始化 sACN 发送器
        
        Args:
            source_name: sACN 源名称
            universe_offset: Universe 偏移量（默认 1，将 0 映射到 1）
                           如果应用使用 Universe 0，sACN 会发送到 Universe 1
        """
        self.sender = sacn.sACNsender(source_name=source_name)
        self.sender.start()
        self.activated_universes = set()
        self.universe_offset = universe_offset
        print(f"✅ sACN 发送器已启动: {source_name}")
        if universe_offset != 0:
            print(f"   Universe 映射: 应用 Universe X → sACN Universe X+{universe_offset}")
    
    def _map_universe(self, app_universe: int) -> int:
        """将应用层的 Universe 映射到 sACN Universe"""
        return app_universe + self.universe_offset
    
    def activate_universe(self, app_universe: int):
        """
        激活一个 DMX Universe
        
        Args:
            app_universe: 应用层 Universe 编号（可以从 0 开始）
        """
        sacn_universe = self._map_universe(app_universe)
        
        if sacn_universe not in self.activated_universes:
            self.sender.activate_output(sacn_universe)
            self.sender[sacn_universe].multicast = True  # 使用组播模式
            self.activated_universes.add(sacn_universe)
            print(f"   已激活 Universe {app_universe} (sACN Universe {sacn_universe})")
    
    def send_dmx(self, app_universe: int, dmx_data: List[int]):
        """
        发送 DMX 数据到指定 Universe
        
        Args:
            app_universe: 应用层 Universe 编号
            dmx_data: DMX 数据列表（512 个通道，每个值 0-255）
        """
        sacn_universe = self._map_universe(app_universe)
        
        # 确保 Universe 已激活
        if sacn_universe not in self.activated_universes:
            self.activate_universe(app_universe)
        
        # sACN 要求 512 个通道的数据
        dmx_512 = [0] * 512
        dmx_512[:len(dmx_data)] = dmx_data
        
        # 发送数据
        self.sender[sacn_universe].dmx_data = tuple(dmx_512)
    
    def send_multiple(self, dmx_data_list: List[Dict]):
        """
        批量发送多个灯具的 DMX 数据
        
        Args:
            dmx_data_list: 包含多个灯具数据的列表，每个元素格式：
                {
                    "universe": 0,
                    "address": 1,
                    "dmx_values": [255, 128, ...]
                }
        """
        # 按 Universe 分组数据
        universes_data = {}
        
        for item in dmx_data_list:
            app_universe = item["universe"]
            address = item["address"]
            values = item["dmx_values"]
            
            if app_universe not in universes_data:
                universes_data[app_universe] = [0] * 512
            
            # 将灯具的通道值写入对应的 DMX 地址
            for i, val in enumerate(values):
                dmx_address = address + i - 1  # DMX 地址从 1 开始
                if 0 <= dmx_address < 512:
                    universes_data[app_universe][dmx_address] = val
        
        # 发送每个 Universe 的数据
        for app_universe, dmx_data in universes_data.items():
            self.send_dmx(app_universe, dmx_data)

    
    def stop(self):
        """停止 sACN 发送器"""
        print("\n⏹ 正在停止 sACN 发送器...")
        self.sender.stop()
        print("✅ sACN 发送器已停止")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def test_sacn_sender():
    """测试 sACN 发送器"""
    print("=" * 60)
    print("sACN 发送器测试")
    print("=" * 60)
    
    with SACNSender(source_name="Test Sender") as sender:
        # 激活 Universe 0
        sender.activate_universe(0)
        
        # 发送测试数据（所有通道设为 128）
        test_data = [128] * 512
        
        print("\n发送测试数据（5 秒）...")
        for i in range(50):
            sender.send_dmx(0, test_data)
            time.sleep(0.1)
        
        print("\n✅ 测试完成")


# if __name__ == "__main__":
#     test_sacn_sender()
