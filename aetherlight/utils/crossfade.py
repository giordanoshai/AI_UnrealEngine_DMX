# aetherlight/utils/crossfade.py
"""
Crossfade 和 Ease 函数工具
用于 cue 之间的平滑过渡
"""
import math
from typing import List, Dict, Callable


def crossfade(dmx_a: list, dmx_b: list, blend: float) -> list:
    """
    在两个 DMX 帧之间执行线性插值
    
    Args:
        dmx_a: DMX 帧 A (512 个值)
        dmx_b: DMX 帧 B (512 个值)
        blend: 混合比例 (0.0 = 全 A, 1.0 = 全 B)
        
    Returns:
        list: 插值后的 DMX 帧
    """
    # 确保 blend 在 0.0-1.0 范围内
    blend = max(0.0, min(1.0, blend))
    
    # 确保两个列表长度一致
    max_len = max(len(dmx_a), len(dmx_b))
    dmx_a_padded = dmx_a + [0] * (max_len - len(dmx_a))
    dmx_b_padded = dmx_b + [0] * (max_len - len(dmx_b))
    
    # 线性插值
    return [int(a + (b - a) * blend) for a, b in zip(dmx_a_padded, dmx_b_padded)]


def should_crossfade_channel(channel_name: str, channel_config: dict) -> bool:
    """
    判断通道是否应该执行 crossfade
    
    discrete 通道(color_wheel, gobo_wheel)不做 crossfade
    
    Args:
        channel_name: 通道名称
        channel_config: 通道配置字典
        
    Returns:
        bool: True 表示应该 crossfade,False 表示应该 CUT
    """
    ch_config = channel_config.get(channel_name, {})
    return ch_config.get("type") != "discrete"


# ========================================
# Ease 函数
# ========================================

def ease_linear(t: float) -> float:
    """线性 ease (无加速/减速)"""
    return t


def ease_in_quad(t: float) -> float:
    """二次方 ease-in (慢速开始,加速)"""
    return t * t


def ease_out_quad(t: float) -> float:
    """二次方 ease-out (快速开始,减速)"""
    return t * (2 - t)


def ease_in_out_quad(t: float) -> float:
    """二次方 ease-in-out (慢速开始和结束,中间加速)"""
    if t < 0.5:
        return 2 * t * t
    else:
        return -1 + (4 - 2 * t) * t


def ease_in_cubic(t: float) -> float:
    """三次方 ease-in"""
    return t * t * t


def ease_out_cubic(t: float) -> float:
    """三次方 ease-out"""
    return (t - 1) * (t - 1) * (t - 1) + 1


def ease_in_out_cubic(t: float) -> float:
    """三次方 ease-in-out"""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return (t - 1) * (2 * t - 2) * (2 * t - 2) + 1


def ease_in_sine(t: float) -> float:
    """正弦 ease-in"""
    return 1 - math.cos(t * math.pi / 2)


def ease_out_sine(t: float) -> float:
    """正弦 ease-out"""
    return math.sin(t * math.pi / 2)


def ease_in_out_sine(t: float) -> float:
    """正弦 ease-in-out"""
    return -(math.cos(math.pi * t) - 1) / 2


# Ease 函数注册表
EASE_FUNCTIONS: Dict[str, Callable[[float], float]] = {
    "linear": ease_linear,
    "ease_in_quad": ease_in_quad,
    "ease_out_quad": ease_out_quad,
    "ease_in_out_quad": ease_in_out_quad,
    "ease_in_cubic": ease_in_cubic,
    "ease_out_cubic": ease_out_cubic,
    "ease_in_out_cubic": ease_in_out_cubic,
    "ease_in_sine": ease_in_sine,
    "ease_out_sine": ease_out_sine,
    "ease_in_out_sine": ease_in_out_sine,
}


def apply_ease(t: float, ease_type: str = "linear") -> float:
    """
    应用 ease 函数到时间值
    
    Args:
        t: 时间值 (0.0 到 1.0)
        ease_type: ease 函数类型
        
    Returns:
        float: ease 后的值 (0.0 到 1.0)
    """
    t = max(0.0, min(1.0, t))  # 确保在 0-1 范围内
    
    ease_func = EASE_FUNCTIONS.get(ease_type, ease_linear)
    return ease_func(t)


def crossfade_with_ease(dmx_a: list, dmx_b: list, blend: float, ease_type: str = "linear") -> list:
    """
    使用 ease 函数的 crossfade
    
    Args:
        dmx_a: DMX 帧 A
        dmx_b: DMX 帧 B
        blend: 混合比例 (0.0 到 1.0)
        ease_type: ease 函数类型
        
    Returns:
        list: 插值后的 DMX 帧
    """
    eased_blend = apply_ease(blend, ease_type)
    return crossfade(dmx_a, dmx_b, eased_blend)
