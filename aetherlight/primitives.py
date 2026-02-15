# primitives.py
import math


def anim_static(t: float, params: dict):
    """固定值"""
    return params.get("value", 1.0)


def anim_wave(t: float, params: dict) -> float:
    """正弦波: min~max 之间平滑摆动"""
    speed = params.get("speed", 0.25)
    min_v = params.get("min", 0.0)
    max_v = params.get("max", 1.0)
    phase = params.get("phase", 0.0)
    sine = 0.5 + 0.5 * math.sin(2 * math.pi * speed * t + phase * 2 * math.pi)
    return min_v + (max_v - min_v) * sine


def anim_pulse(t: float, params: dict) -> float:
    """方波: 在 min/max 之间突变跳动"""
    speed = params.get("speed", 1.0)
    min_v = params.get("min", 0.0)
    max_v = params.get("max", 1.0)
    duty = params.get("duty_cycle", 0.5)
    phase = params.get("phase", 0.0)
    pos = (t * speed + phase) % 1.0
    return max_v if pos < duty else min_v


def anim_ramp(t: float, params: dict) -> float:
    """锯齿波: 线性递增后跳回"""
    speed = params.get("speed", 0.2)
    min_v = params.get("min", 0.0)
    max_v = params.get("max", 1.0)
    phase = params.get("phase", 0.0)
    pos = (t * speed + phase) % 1.0
    return min_v + (max_v - min_v) * pos


def anim_step(t: float, params: dict):
    """阶梯跳变: 按顺序在多个值之间循环"""
    values = params.get("values", [])
    hold_time = params.get("hold_time", 1.0)
    phase = params.get("phase", 0.0)
    if not values:
        return 0
    n = len(values)
    index = int((t / hold_time + phase * n) % n)
    return values[index]


# 动画注册表
ANIMATIONS = {
    "static": anim_static,
    "wave": anim_wave,
    "pulse": anim_pulse,
    "ramp": anim_ramp,
    "step": anim_step,
}