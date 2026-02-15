# test_spatial_simple.py
"""
简化版测试 - 验证 spatial.py 的核心功能
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from aetherlight.spatial import auto_detect_axis, sort_fixtures_by_axis


def test_sorting_and_axis():
    """测试坐标排序和轴检测的核心功能"""
    
    print("="*70)
    print("测试 1: X 轴排序验证")
    print("="*70)
    
    # 测试 X 轴排序
    fixtures_x = [
        {"name": "F3", "position": [3.0, 0.0, 0.0]},
        {"name": "F1", "position": [1.0, 0.0, 0.0]},
        {"name": "F5", "position": [5.0, 0.0, 0.0]},
        {"name": "F2", "position": [2.0, 0.0, 0.0]},
        {"name": "F4", "position": [4.0, 0.0, 0.0]},
    ]
    
    print("原始顺序:", [f["name"] for f in fixtures_x])
    sorted_fixtures, axis = sort_fixtures_by_axis(fixtures_x, axis="x")
    print(f"排序后:  {[f['name'] for f in sorted_fixtures]}")
    print(f"使用轴:  {axis}")
    
    # 验证排序正确性
    expected_order = ["F1", "F2", "F3", "F4", "F5"]
    actual_order = [f["name"] for f in sorted_fixtures]
    assert actual_order == expected_order, f"排序错误！期望: {expected_order}, 实际: {actual_order}"
    
    # 验证 phase 值
    phases = [f["phase"] for f in sorted_fixtures]
    print(f"Phase 值: {phases}")
    assert phases[0] == 0.0, "第一个 phase 应该是 0.0"
    assert phases[-1] == 1.0, "最后一个 phase 应该是 1.0"
    assert all(phases[i] <= phases[i+1] for i in range(len(phases)-1)), "Phase 应该递增"
    
    print("✅ X 轴排序正确！Phase 归一化正确！\n")
    
    # ====================================================================
    
    print("="*70)
    print("测试 2: 自动检测 - 单轴分布")
    print("="*70)
    
    # Y 轴分布
    fixtures_y = [
        {"name": "A", "position": [0.0, 1.0, 0.0]},
        {"name": "B", "position": [0.0, 2.0, 0.0]},
        {"name": "C", "position": [0.0, 3.0, 0.0]},
        {"name": "D", "position": [0.0, 4.0, 0.0]},
        {"name": "E", "position": [0.0, 5.0, 0.0]},
    ]
    
    detected_axis = auto_detect_axis(fixtures_y)
    print(f"Y 轴分布的灯具，检测到的轴: {detected_axis}")
    assert detected_axis == "y", f"应该检测为 Y 轴，但检测为 {detected_axis}"
    print("✅ 自动检测到 Y 轴正确！\n")
    
    # Z 轴分布
    fixtures_z = [
        {"name": "L1", "position": [0.0, 0.0, 1.0]},
        {"name": "L2", "position": [0.0, 0.0, 2.0]},
        {"name": "L3", "position": [0.0, 0.0, 3.0]},
    ]
    
    detected_axis = auto_detect_axis(fixtures_z)
    print(f"Z 轴分布的灯具，检测到的轴: {detected_axis}")
    assert detected_axis == "z", f"应该检测为 Z 轴，但检测为 {detected_axis}"
    print("✅ 自动检测到 Z 轴正确！\n")
    
    # ====================================================================
    
    print("="*70)
    print("测试 3: 自动检测 - 平面分布（应该检测为 radial）")
    print("="*70)
    
    # XY 平面分布
    fixtures_plane = [
        {"name": "P1", "position": [1.0, 1.0, 0.0]},
        {"name": "P2", "position": [2.0, 1.5, 0.0]},
        {"name": "P3", "position": [1.5, 2.0, 0.0]},
        {"name": "P4", "position": [3.0, 2.5, 0.0]},
        {"name": "P5", "position": [2.5, 3.0, 0.0]},
        {"name": "P6", "position": [1.0, 3.0, 0.0]},
    ]
    
    # 计算方差
    n = len(fixtures_plane)
    positions = [f["position"] for f in fixtures_plane]
    mean_x = sum(p[0] for p in positions) / n
    mean_y = sum(p[1] for p in positions) / n
    mean_z = sum(p[2] for p in positions) / n
    
    var_x = sum((p[0] - mean_x) ** 2 for p in positions) / n
    var_y = sum((p[1] - mean_y) ** 2 for p in positions) / n
    var_z = sum((p[2] - mean_z) ** 2 for p in positions) / n
    
    print(f"X 轴方差: {var_x:.4f}")
    print(f"Y 轴方差: {var_y:.4f}")
    print(f"Z 轴方差: {var_z:.4f}")
    
    sorted_vars = sorted([var_x, var_y, var_z], reverse=True)
    ratio = sorted_vars[1] / sorted_vars[0] if sorted_vars[0] > 0 else 0
    print(f"最大两个方差比值: {ratio:.4f} (阈值: 0.5)")
    
    detected_axis = auto_detect_axis(fixtures_plane)
    print(f"检测到的轴: {detected_axis}")
    
    if ratio > 0.5:
        assert detected_axis == "radial", f"比值 > 0.5，应该检测为 radial，但检测为 {detected_axis}"
        print("✅ 正确检测为平面分布（radial）！\n")
    else:
        print(f"⚠️  比值 ≤ 0.5，检测为单轴 {detected_axis}\n")
    
    # ====================================================================
    
    print("="*70)
    print("测试 4: Auto 模式测试")
    print("="*70)
    
    sorted_auto, auto_axis = sort_fixtures_by_axis(fixtures_x, axis="auto")
    print(f"X 轴数据使用 auto 模式，检测到: {auto_axis}")
    assert auto_axis == "x", f"应该自动检测为 X 轴"
    print("✅ Auto 模式正确！\n")
    
    # ====================================================================
    
    print("="*70)
    print("📊 测试总结")
    print("="*70)
    print("✅ 1. 坐标排序功能正常")
    print("✅ 2. Phase 归一化计算正确（0.0 到 1.0）")
    print("✅ 3. 自动轴检测正常（X/Y/Z 单轴）")
    print("✅ 4. 平面分布检测正常（radial）")
    print("✅ 5. Auto 模式工作正常")
    print("\n🎉 所有测试通过！spatial.py 功能正常！")


# if __name__ == "__main__":
#     test_sorting_and_axis()
import json
def get_test_config():
    with open("projects/TEST1.json", "r") as f:
        data = json.load(f)
    
    fixtures = data["fixtures"]
    
    return fixtures

test_config = get_test_config()

detected_axis = auto_detect_axis(test_config)

sorted_fixtures, axis = sort_fixtures_by_axis(test_config, axis=detected_axis)

print(axis)

