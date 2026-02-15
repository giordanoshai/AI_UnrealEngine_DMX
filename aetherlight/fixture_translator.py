# fixture_translator.py
import time
from aetherlight.primitives import ANIMATIONS
from aetherlight.spatial import sort_fixtures_by_axis


class EffectTranslator:
    """
    统一的效果翻译引擎。
    - 接收灯具列表（1 盏或 N 盏均可）
    - 支持 phase: "auto" 自动按空间排序分配
    - 支持 phase_axis 自动检测或手动指定
    """

    def __init__(self, fixtures: list, channel_config: dict):
        """
        fixtures:       灯具列表 (从 UE 导出的 JSON)
        channel_config:  通道配置 (FIXTURE_CONFIG["channels"])
        """
        self.fixtures = fixtures
        self.channel_config = channel_config
        self.effect = None
        self.sorted_fixtures = []
        self.active_axis = None

    def load_effect(self, effect_json: dict):
        """加载效果，自动（或按指定）排序灯具"""
        self.effect = effect_json

        # phase_axis: 省略 / "auto" → 自动检测; "x"/"y"/"z"/... → 手动指定
        axis = effect_json.get("phase_axis", "auto")
        self.sorted_fixtures, self.active_axis = sort_fixtures_by_axis(
            [f.copy() for f in self.fixtures],
            axis=axis
        )

        print(f"✅ 已加载效果: {effect_json.get('effect_name')}")
        print(f"   排序轴: {self.active_axis}"
              f"{'（自动检测）' if axis in (None, 'auto') else ''}")
        for f in self.sorted_fixtures:
            print(f"   {f['name']:10s}  phase={f['phase']:.3f}  "
                  f"pos=({f['position'][0]:.0f}, {f['position'][1]:.0f}, {f['position'][2]:.0f})")

    def evaluate_fixture(self, fixture: dict, t: float) -> dict:
        """计算单个灯具在时间 t 的所有通道值"""
        fixture_phase = fixture.get("phase", 0.0)
        result = {}

        for prim in self.effect.get("primitives", []):
            ch_name = prim["channel"]
            anim_name = prim["animation"]
            params = prim.get("params", {}).copy()

            if anim_name not in ANIMATIONS:
                continue

            # ★ phase 为 "auto" 时，替换为灯具的空间 phase
            if params.get("phase") == "auto":
                params["phase"] = fixture_phase

            result[ch_name] = ANIMATIONS[anim_name](t, params)

        return result

    def to_dmx_frame(self, t: float) -> dict:
        """
        计算所有灯具在时间 t 的 DMX 值。
        返回: { universe: { address: [ch0, ch1, ...] } }
        """
        frame = {}

        for fixture in self.sorted_fixtures:
            universe = fixture.get("universe", 0)
            address = fixture.get("address", 1)
            values = self.evaluate_fixture(fixture, t)

            # 使用字典存储 {offset: dmx_value}，然后按offset排序构建数组
            dmx_dict = {}
            
            for ch_name, ch_config in self.channel_config.items():
                # 如果 effect 中没有定义该通道，使用配置中的默认值
                if ch_name in values:
                    raw = values.get(ch_name)
                else:
                    raw = ch_config.get("default_value", 0)
                
                # 获取通道偏移量（如果有定义）
                offset = ch_config.get("offset", len(dmx_dict))
                
                if ch_config["type"] == "continuous":
                    clamped = max(0.0, min(1.0, float(raw)))
                    dmx_dict[offset] = int(clamped * 255)
                elif ch_config["type"] == "discrete":
                    mapping = ch_config.get("mapping", {})
                    if isinstance(raw, str) and raw in mapping:
                        dmx_dict[offset] = mapping[raw]
                    else:
                        dmx_dict[offset] = int(raw) if isinstance(raw, (int, float)) else 0
            
            # 将字典转换为按offset排序的数组
            if dmx_dict:
                max_offset = max(dmx_dict.keys())
                dmx = [0] * (max_offset + 1)  # offset是0-based，所以需要+1
                for offset, value in dmx_dict.items():
                    dmx[offset] = value
            else:
                dmx = []

            if universe not in frame:
                frame[universe] = {}
            frame[universe][address] = dmx

        return frame

    def to_artnet_packets(self, t: float) -> dict:
        """
        生成可直接发送的 Art-Net 数据包。
        返回: { universe: [512 个 DMX 值] }
        """
        frame = self.to_dmx_frame(t)
        packets = {}

        for universe, fixtures_data in frame.items():
            packet = [0] * 512
            for address, dmx_values in fixtures_data.items():
                for i, val in enumerate(dmx_values):
                    idx = address - 1 + i
                    if 0 <= idx < 512:
                        packet[idx] = val
            packets[universe] = packet

        return packets