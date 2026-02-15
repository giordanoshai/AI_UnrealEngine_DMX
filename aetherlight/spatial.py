# spatial.py
import math
from typing import List, Dict, Literal, Optional


def auto_detect_axis(fixtures: List[Dict]) -> str:
    """
    根据灯具坐标的方差分布，自动检测最佳排序轴。

    规则：
    - 计算 X/Y/Z 三轴方差
    - 如果两个最大方差的比值 > 0.5 → 灯具在平面上分布 → 用 radial
    - 否则 → 选方差最大的单轴
    """
    if len(fixtures) < 2:
        return "x"

    positions = [f["position"] for f in fixtures]
    n = len(positions)

    # 各轴均值
    mean_x = sum(p[0] for p in positions) / n
    mean_y = sum(p[1] for p in positions) / n
    mean_z = sum(p[2] for p in positions) / n

    # 各轴方差
    var_x = sum((p[0] - mean_x) ** 2 for p in positions) / n
    var_y = sum((p[1] - mean_y) ** 2 for p in positions) / n
    var_z = sum((p[2] - mean_z) ** 2 for p in positions) / n

    variances = {"x": var_x, "y": var_y, "z": var_z}
    sorted_vars = sorted(variances.values(), reverse=True)

    # 两个最大方差接近 → 平面分布 → radial
    if sorted_vars[0] > 0 and sorted_vars[1] / sorted_vars[0] > 0.5:
        return "radial"

    # 否则取方差最大的轴
    return max(variances, key=variances.get)


def sort_fixtures_by_axis(
    fixtures: List[Dict],
    axis: Optional[str] = None
) -> tuple:
    """
    按空间轴排序灯具，并为每个灯具计算归一化的 phase (0~1)。

    fixtures: 灯具列表，每个灯具须有 "position": [x, y, z]
    axis:     排序方式。None 或 "auto" 时自动检测。
    返回:     (排序后的灯具列表, 实际使用的 axis)
    """
    if not fixtures:
        return [], "x"

    # 自动检测
    if axis is None or axis == "auto":
        axis = auto_detect_axis(fixtures)

    # --- 计算灯组中心点 ---
    n = len(fixtures)
    cx = sum(f["position"][0] for f in fixtures) / n
    cy = sum(f["position"][1] for f in fixtures) / n
    cz = sum(f["position"][2] for f in fixtures) / n

    # --- 排序键函数 ---
    def get_sort_key(f):
        x, y, z = f["position"]
        if axis == "x":
            return x
        elif axis == "y":
            return y
        elif axis == "z":
            return z
        elif axis == "radial":
            return math.sqrt((x - cx)**2 + (y - cy)**2 + (z - cz)**2)
        elif axis == "angle":
            return math.atan2(y - cy, x - cx)
        else:
            return x

    # --- 排序 ---
    sorted_fixtures = sorted(fixtures, key=get_sort_key)

    # --- 归一化为 0~1 的 phase ---
    if n == 1:
        sorted_fixtures[0]["phase"] = 0.0
    else:
        keys = [get_sort_key(f) for f in sorted_fixtures]
        min_k = min(keys)
        max_k = max(keys)
        range_k = max_k - min_k if max_k != min_k else 1.0

        for i, f in enumerate(sorted_fixtures):
            f["phase"] = (keys[i] - min_k) / range_k

    return sorted_fixtures, axis