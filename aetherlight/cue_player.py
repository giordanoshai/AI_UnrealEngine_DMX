# aetherlight/cue_player.py
"""
Cue Player - 灯光 Cue 播放控制系统
支持多效果连续播放、切换效果、多 group 管理
"""
import time
import threading
from typing import Dict, List, Optional, Any
from aetherlight.fixture_translator import EffectTranslator
from aetherlight.sacn_sender import SACNSender
from aetherlight.database.database import get_effect
from aetherlight.utils.crossfade import crossfade_with_ease, EASE_FUNCTIONS


class CuePlayer:
    """
    Cue Player 主类
    
    功能:
    - 播放 cue list (顺序播放多个 effect)
    - 支持 play/pause/stop/resume 控制
    - 支持 CUT/FADE 切换效果
    - 支持多 group 同时播放
    - 支持循环播放
    """
    
    def __init__(self, sacn_sender: SACNSender, fixtures: List[Dict], channel_config: Dict, fps: int = 30):
        """
        初始化 CuePlayer
        
        Args:
            sacn_sender: SACNSender 实例
            fixtures: 灯具列表
            channel_config: 通道配置
            fps: 帧率 (默认 30)
        """
        self.sacn_sender = sacn_sender
        self.fixtures = fixtures
        self.channel_config = channel_config
        self.fps = fps
        self.frame_time = 1.0 / fps
        
        # Cue List 数据
        self.cue_list: List[Dict] = []
        self.loop = False
        
        # 播放状态
        self.is_playing = False
        self.is_paused = False
        self.current_cue_index = 0
        self.cue_start_time = 0.0  # 当前 cue 的开始时间
        self.pause_time = 0.0  # 暂停时的时间
        
        # Effect 相关
        self.current_effect: Optional[Dict] = None
        self.next_effect: Optional[Dict] = None
        self.current_translator: Optional[EffectTranslator] = None
        self.next_translator: Optional[EffectTranslator] = None
        
        # 切换相关
        self.is_transitioning = False
        self.transition_start_time = 0.0
        self.transition_duration = 0.0
        self.transition_ease = "linear"
        
        # 播放线程
        self.playback_thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()
        
        # 多 Group 支持 (预留,当前版本单 group)
        self.active_groups: Dict[str, Dict] = {}
    
    def load_cue_list(self, cue_list_data: Dict):
        """
        加载 cue list
        
        Args:
            cue_list_data: Cue list 数据字典
                {
                    "cue_list_name": "示例演出",
                    "cues": [
                        {
                            "cue_number": 1,
                            "effect_id": "uuid" or "effect_name",
                            "groups": ["group1"],
                            "transition_type": "FADE" or "CUT",
                            "fade_time": 2.0,
                            "ease_type": "ease_in_out_quad"
                        },
                        ...
                    ],
                    "loop": False
                }
        """
        self.cue_list = cue_list_data.get("cues", [])
        self.loop = cue_list_data.get("loop", False)
        self.current_cue_index = 0
        
        print(f"✅ 已加载 Cue List: {cue_list_data.get('cue_list_name', 'Unnamed')}")
        print(f"   Cue 数量: {len(self.cue_list)}")
        print(f"   循环播放: {'是' if self.loop else '否'}")
    
    def _load_effect_from_cue(self, cue: Dict) -> Optional[Dict]:
        """
        从 cue 配置加载 effect
        
        Args:
            cue: Cue 配置字典
            
        Returns:
            Effect 数据,失败返回 None
        """
        # 优先使用 effect_data (内存中的 effect)
        if "effect_data" in cue:
            return cue["effect_data"]
        
        # 否则从数据库加载
        effect_id = cue.get("effect_id")
        
        if not effect_id:
            print("❌ Cue 中既没有 effect_data 也没有 effect_id")
            return None
        
        # 如果是 UUID,从数据库加载
        if isinstance(effect_id, str) and len(effect_id) == 36:  # UUID 长度
            effect = get_effect(effect_id=effect_id)
            if effect:
                return effect
        
        # 否则按名称从数据库加载
        effect = get_effect(effect_name=effect_id)
        return effect
    
    def play(self):
        """开始播放 cue list"""
        if not self.cue_list:
            print("❌ Cue List 为空,无法播放")
            return
        
        if self.is_playing:
            print("⚠️  已在播放中")
            return
        
        # 重置状态
        self.is_playing = True
        self.is_paused = False
        self.current_cue_index = 0
        self.stop_flag.clear()
        
        # 启动播放线程
        self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.playback_thread.start()
        
        print("▶️  开始播放 Cue List")
    
    def pause(self):
        """暂停播放"""
        if not self.is_playing:
            print("⚠️  未在播放中")
            return
        
        if self.is_paused:
            print("⚠️  已暂停")
            return
        
        self.is_paused = True
        self.pause_time = time.time()
        print("⏸️  暂停播放")
    
    def resume(self):
        """继续播放"""
        if not self.is_playing:
            print("⚠️  未在播放中")
            return
        
        if not self.is_paused:
            print("⚠️  未暂停")
            return
        
        # 调整时间偏移
        pause_duration = time.time() - self.pause_time
        self.cue_start_time += pause_duration
        if self.is_transitioning:
            self.transition_start_time += pause_duration
        
        self.is_paused = False
        print("▶️  继续播放")
    
    def stop(self):
        """停止播放"""
        if not self.is_playing:
            print("⚠️  未在播放中")
            return
        
        self.is_playing = False
        self.is_paused = False
        self.stop_flag.set()
        
        # 等待线程结束 (只有在不是当前线程时才 join)
        if self.playback_thread and threading.current_thread() != self.playback_thread:
            self.playback_thread.join(timeout=2.0)
        
        # 清空 DMX 输出
        self._send_blackout()
        
        print("⏹️  停止播放")
    
    def next_cue(self):
        """跳到下一个 cue"""
        if not self.is_playing:
            print("⚠️  未在播放中")
            return
        
        self.current_cue_index += 1
        if self.current_cue_index >= len(self.cue_list):
            if self.loop:
                self.current_cue_index = 0
            else:
                self.stop()
                print("✅ Cue List 播放完成")
                return
        
        self._start_cue(self.current_cue_index)
        print(f"⏭️  跳到 Cue #{self.current_cue_index + 1}")
    
    def prev_cue(self):
        """跳到上一个 cue"""
        if not self.is_playing:
            print("⚠️  未在播放中")
            return
        
        self.current_cue_index = max(0, self.current_cue_index - 1)
        self._start_cue(self.current_cue_index)
        print(f"⏮️  跳到 Cue #{self.current_cue_index + 1}")
    
    def goto_cue(self, cue_number: int):
        """
        跳到指定 cue
        
        Args:
            cue_number: Cue 编号 (从 1 开始)
        """
        if not self.is_playing:
            print("⚠️  未在播放中")
            return
        
        cue_index = cue_number - 1
        if 0 <= cue_index < len(self.cue_list):
            self.current_cue_index = cue_index
            self._start_cue(self.current_cue_index)
            print(f"⏩ 跳到 Cue #{cue_number}")
        else:
            print(f"❌ Cue #{cue_number} 不存在")
    
    def _start_cue(self, cue_index: int):
        """
        开始播放指定 cue
        
        Args:
            cue_index: Cue 索引
        """
        cue = self.cue_list[cue_index]
        
        # 加载 effect
        effect = self._load_effect_from_cue(cue)
        if not effect:
            print(f"❌ 无法加载 Cue #{cue_index + 1} 的 effect: {cue.get('effect_id')}")
            return
        
        # 检查切换类型
        transition_type = cue.get("transition_type", "CUT").upper()
        
        if transition_type == "FADE" and self.current_translator is not None:
            # FADE 切换
            self.is_transitioning = True
            self.transition_start_time = time.time()
            self.transition_duration = cue.get("fade_time", 1.0)
            self.transition_ease = cue.get("ease_type", "linear")
            
            # 保存下一个 effect
            self.next_effect = effect
            self.next_translator = EffectTranslator(self.fixtures, self.channel_config)
            self.next_translator.load_effect(effect)
        else:
            # CUT 切换
            self.current_effect = effect
            self.current_translator = EffectTranslator(self.fixtures, self.channel_config)
            self.current_translator.load_effect(effect)
            self.is_transitioning = False
        
        self.cue_start_time = time.time()
        
        print(f"🎬 播放 Cue #{cue_index + 1}: {effect.get('effect_name')} "
              f"({transition_type}, {effect.get('duration')}s)")
    
    def _playback_loop(self):
        """播放循环 (在独立线程中运行)"""
        # 开始第一个 cue
        self._start_cue(self.current_cue_index)
        
        while self.is_playing and not self.stop_flag.is_set():
            if self.is_paused:
                time.sleep(0.1)
                continue
            
            loop_start = time.time()
            
            # 计算当前时间
            current_time = time.time()
            cue_elapsed = current_time - self.cue_start_time
            
            # 生成 DMX 数据
            packets = self._generate_dmx_frame(cue_elapsed)
            
            # 发送 DMX
            for universe, dmx_data in packets.items():
                self.sacn_sender.send_dmx(universe, dmx_data)
            
            # 检查是否需要切换到下一个 cue
            if not self.is_transitioning:
                effect_duration = self.current_effect.get("duration", 10.0)
                if cue_elapsed >= effect_duration:
                    # 当前 cue 播放完成,切换到下一个
                    self.current_cue_index += 1
                    if self.current_cue_index >= len(self.cue_list):
                        if self.loop:
                            self.current_cue_index = 0
                            self._start_cue(self.current_cue_index)
                        else:
                            print("✅ Cue List 播放完成")
                            self.stop()
                            break
                    else:
                        self._start_cue(self.current_cue_index)
            
            # 控制帧率
            elapsed = time.time() - loop_start
            sleep_time = max(0, self.frame_time - elapsed)
            time.sleep(sleep_time)
    
    def _generate_dmx_frame(self, t: float) -> Dict[int, List[int]]:
        """
        生成当前时刻的 DMX 帧
        
        Args:
            t: 当前 cue 的播放时间(秒)
            
        Returns:
            {universe: [512 个 DMX 值]}
        """
        if self.is_transitioning:
            # FADE 切换中
            transition_elapsed = time.time() - self.transition_start_time
            progress = min(1.0, transition_elapsed / self.transition_duration)
            
            # 生成两个 effect 的 DMX 帧
            packets_a = self.current_translator.to_artnet_packets(t)
            packets_b = self.next_translator.to_artnet_packets(0.0)  # 新 effect 从 0 开始
            
            # Crossfade
            merged_packets = {}
            for universe in set(packets_a.keys()) | set(packets_b.keys()):
                dmx_a = packets_a.get(universe, [0] * 512)
                dmx_b = packets_b.get(universe, [0] * 512)
                merged_packets[universe] = crossfade_with_ease(dmx_a, dmx_b, progress, self.transition_ease)
            
            # 切换完成
            if progress >= 1.0:
                self.current_effect = self.next_effect
                self.current_translator = self.next_translator
                self.next_effect = None
                self.next_translator = None
                self.is_transitioning = False
                self.cue_start_time = time.time()  # 重置开始时间
            
            return merged_packets
        else:
            # 正常播放
            if self.current_translator:
                return self.current_translator.to_artnet_packets(t)
            else:
                return {}
    
    def _send_blackout(self):
        """发送黑场 (全 0)"""
        universes = set(f.get('universe', 0) for f in self.fixtures)
        for universe in universes:
            self.sacn_sender.send_dmx(universe, [0] * 512)
