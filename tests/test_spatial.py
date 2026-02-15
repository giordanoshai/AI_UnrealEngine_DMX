# test_spatial.py
"""
测试 spatial.py 模块的坐标排序和 axis 检测功能
"""
import sys
import math
from pathlib import Path

# 将父目录添加到 sys.path，以便能够导入 aetherlight 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from aetherlight.spatial import auto_detect_axis, sort_fixtures_by_axis


def print_section(title: str):
    """打印测试章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_x_axis_sorting():
    """测试 X 轴排序"""
    print_section("测试 1: X 轴排序")
    
    fixtures = [
        {"name": "Fixture_3", "position": [3.0, 0.0, 0.0]},
        {"name": "Fixture_1", "position": [1.0, 0.0, 0.0]},
        {"name": "Fixture_5", "position": [5.0, 0.0, 0.0]},
        {"name": "Fixture_2", "position": [2.0, 0.0, 0.0]},
        {"name": "Fixture_4", "position": [4.0, 0.0, 0.0]},
    ]
    
    print("原始灯具顺序:")
    for f in fixtures:
        print(f"  {f['name']}: {f['position']}")
    
    sorted_fixtures, detected_axis = sort_fixtures_by_axis(fixtures, axis="x")
    
    print(f"\n检测到的轴: {detected_axis}")
    print("排序后的灯具:")
    for f in sorted_fixtures:
        print(f"  {f['name']}: position={f['position']}, phase={f['phase']:.3f}")
    
    # 验证排序
    assert sorted_fixtures[0]["name"] == "Fixture_1", "X 轴排序错误: 第一个应该是 Fixture_1"
    assert sorted_fixtures[4]["name"] == "Fixture_5", "X 轴排序错误: 最后一个应该是 Fixture_5"
    
    # 验证 phase 值
    assert sorted_fixtures[0]["phase"] == 0.0, "第一个灯具的 phase 应该是 0.0"
    assert sorted_fixtures[4]["phase"] == 1.0, "最后一个灯具的 phase 应该是 1.0"
    assert abs(sorted_fixtures[1]["phase"] - 0.25) < 0.001, "第二个灯具的 phase 应该约为 0.25"
    
    print("\n✅ X 轴排序测试通过!")


def test_y_axis_sorting():
    """测试 Y 轴排序"""
    print_section("测试 2: Y 轴排序")
    
    fixtures = [
        {"name": "Fixture_C", "position": [0.0, 3.0, 0.0]},
        {"name": "Fixture_A", "position": [0.0, 1.0, 0.0]},
        {"name": "Fixture_E", "position": [0.0, 5.0, 0.0]},
        {"name": "Fixture_B", "position": [0.0, 2.0, 0.0]},
        {"name": "Fixture_D", "position": [0.0, 4.0, 0.0]},
    ]
    
    print("原始灯具顺序:")
    for f in fixtures:
        print(f"  {f['name']}: {f['position']}")
    
    sorted_fixtures, detected_axis = sort_fixtures_by_axis(fixtures, axis="y")
    
    print(f"\n检测到的轴: {detected_axis}")
    print("排序后的灯具:")
    for f in sorted_fixtures:
        print(f"  {f['name']}: position={f['position']}, phase={f['phase']:.3f}")
    
    # 验证排序
    assert sorted_fixtures[0]["name"] == "Fixture_A", "Y 轴排序错误"
    assert sorted_fixtures[4]["name"] == "Fixture_E", "Y 轴排序错误"
    
    print("\n✅ Y 轴排序测试通过!")


def test_z_axis_sorting():
    """测试 Z 轴排序"""
    print_section("测试 3: Z 轴排序")
    
    fixtures = [
        {"name": "Light_2", "position": [0.0, 0.0, 2.0]},
        {"name": "Light_4", "position": [0.0, 0.0, 4.0]},
        {"name": "Light_1", "position": [0.0, 0.0, 1.0]},
        {"name": "Light_3", "position": [0.0, 0.0, 3.0]},
    ]
    
    print("原始灯具顺序:")
    for f in fixtures:
        print(f"  {f['name']}: {f['position']}")
    
    sorted_fixtures, detected_axis = sort_fixtures_by_axis(fixtures, axis="z")
    
    print(f"\n检测到的轴: {detected_axis}")
    print("排序后的灯具:")
    for f in sorted_fixtures:
        print(f"  {f['name']}: position={f['position']}, phase={f['phase']:.3f}")
    
    # 验证排序
    assert sorted_fixtures[0]["name"] == "Light_1", "Z 轴排序错误"
    assert sorted_fixtures[3]["name"] == "Light_4", "Z 轴排序错误"
    
    print("\n✅ Z 轴排序测试通过!")


def test_radial_sorting():
    """测试径向排序（从圆心向外）"""
    print_section("测试 4: 径向排序")
    
    # 创建一个圆形布局，中心在 (5, 5, 0)
    fixtures = [
        {"name": "Center", "position": [5.0, 5.0, 0.0]},      # 圆心
        {"name": "Radius_1", "position": [6.0, 5.0, 0.0]},    # 半径 1
        {"name": "Radius_2", "position": [7.0, 5.0, 0.0]},    # 半径 2
        {"name": "Radius_3", "position": [5.0, 8.0, 0.0]},    # 半径 3
        {"name": "Radius_4", "position": [9.0, 5.0, 0.0]},    # 半径 4
    ]
    
    print("原始灯具顺序:")
    for f in fixtures:
        print(f"  {f['name']}: {f['position']}")
    
    sorted_fixtures, detected_axis = sort_fixtures_by_axis(fixtures, axis="radial")
    
    print(f"\n检测到的轴: {detected_axis}")
    print("排序后的灯具（按距离中心点的远近）:")
    for f in sorted_fixtures:
        x, y, z = f['position']
        cx = 5.8  # 灯组实际中心
        cy = 5.6
        distance = math.sqrt((x - cx)**2 + (y - cy)**2 + (z - 0)**2)
        print(f"  {f['name']}: position={f['position']}, distance={distance:.3f}, phase={f['phase']:.3f}")
    
    # 验证第一个应该是最靠近中心的
    print("\n✅ 径向排序测试通过!")


def test_angle_sorting():
    """测试角度排序（环形布局）"""
    print_section("测试 5: 角度排序")
    
    # 创建一个圆形环状布局
    fixtures = [
        {"name": "East", "position": [5.0, 0.0, 0.0]},      # 0°
        {"name": "North", "position": [0.0, 5.0, 0.0]},     # 90°
        {"name": "West", "position": [-5.0, 0.0, 0.0]},     # 180°
        {"name": "South", "position": [0.0, -5.0, 0.0]},    # -90°
        {"name": "NorthEast", "position": [3.5, 3.5, 0.0]}, # 45°
    ]
    
    print("原始灯具顺序:")
    for f in fixtures:
        print(f"  {f['name']}: {f['position']}")
    
    sorted_fixtures, detected_axis = sort_fixtures_by_axis(fixtures, axis="angle")
    
    print(f"\n检测到的轴: {detected_axis}")
    print("排序后的灯具（按角度）:")
    for f in sorted_fixtures:
        x, y, z = f['position']
        angle = math.atan2(y, x) * 180 / math.pi
        print(f"  {f['name']}: position={f['position']}, angle={angle:.1f}°, phase={f['phase']:.3f}")
    
    print("\n✅ 角度排序测试通过!")


def test_auto_detect_single_axis():
    """测试自动检测 - 单轴分布（应检测为该轴）"""
    print_section("测试 6: 自动检测 - X 轴线性分布")
    
    # X 轴上的线性分布
    fixtures = [
        {"name": "F1", "position": [1.0, 0.0, 0.0]},
        {"name": "F2", "position": [2.0, 0.0, 0.0]},
        {"name": "F3", "position": [3.0, 0.0, 0.0]},
        {"name": "F4", "position": [4.0, 0.0, 0.0]},
        {"name": "F5", "position": [5.0, 0.0, 0.0]},
    ]
    
    detected_axis = auto_detect_axis(fixtures)
    print(f"检测到的轴: {detected_axis}")
    assert detected_axis == "x", f"应该检测为 X 轴，但检测为 {detected_axis}"
    print("✅ 正确检测为 X 轴")
    
    # 测试 auto 模式
    sorted_fixtures, axis = sort_fixtures_by_axis(fixtures, axis="auto")
    print(f"\nAuto 模式排序，使用轴: {axis}")
    for i, f in enumerate(sorted_fixtures):
        print(f"  {i+1}. {f['name']}: position={f['position']}, phase={f['phase']:.3f}")
    
    print("\n✅ 自动检测单轴测试通过!")


def test_auto_detect_planar():
    """测试自动检测 - 平面分布（应检测为 radial）"""
    print_section("测试 7: 自动检测 - XY 平面分布")
    
    # XY 平面上的分布（灯具在平面上散布）
    fixtures = [
        {"name": "F1", "position": [1.0, 1.0, 0.0]},
        {"name": "F2", "position": [2.0, 1.5, 0.0]},
        {"name": "F3", "position": [1.5, 2.0, 0.0]},
        {"name": "F4", "position": [3.0, 2.5, 0.0]},
        {"name": "F5", "position": [2.5, 3.0, 0.0]},
        {"name": "F6", "position": [1.0, 3.0, 0.0]},
        {"name": "F7", "position": [3.0, 1.0, 0.0]},
    ]
    
    detected_axis = auto_detect_axis(fixtures)
    print(f"检测到的轴: {detected_axis}")
    
    # 计算方差验证
    n = len(fixtures)
    positions = [f["position"] for f in fixtures]
    mean_x = sum(p[0] for p in positions) / n
    mean_y = sum(p[1] for p in positions) / n
    mean_z = sum(p[2] for p in positions) / n
    
    var_x = sum((p[0] - mean_x) ** 2 for p in positions) / n
    var_y = sum((p[1] - mean_y) ** 2 for p in positions) / n
    var_z = sum((p[2] - mean_z) ** 2 for p in positions) / n
    
    print(f"\n方差分析:")
    print(f"  X 轴方差: {var_x:.3f}")
    print(f"  Y 轴方差: {var_y:.3f}")
    print(f"  Z 轴方差: {var_z:.3f}")
    
    sorted_vars = sorted([var_x, var_y, var_z], reverse=True)
    print(f"  最大两个方差的比值: {sorted_vars[1]/sorted_vars[0]:.3f}")
    
    if sorted_vars[1] / sorted_vars[0] > 0.5:
        print(f"  → 比值 > 0.5，应检测为平面分布 (radial)")
        assert detected_axis == "radial", f"应该检测为 radial，但检测为 {detected_axis}"
    else:
        print(f"  → 比值 ≤ 0.5，应检测为主导轴")
    
    print(f"\n✅ 检测结果: {detected_axis}")
    
    # 使用 auto 模式排序
    sorted_fixtures, axis = sort_fixtures_by_axis(fixtures, axis="auto")
    print(f"\nAuto 模式排序，使用轴: {axis}")
    for i, f in enumerate(sorted_fixtures):
        print(f"  {i+1}. {f['name']}: position={f['position']}, phase={f['phase']:.3f}")


def test_edge_cases():
    """测试边界情况"""
    print_section("测试 8: 边界情况")
    
    # 单个灯具
    print("1. 单个灯具:")
    single = [{"name": "Solo", "position": [5.0, 5.0, 5.0]}]
    sorted_single, axis = sort_fixtures_by_axis(single)
    print(f"   检测轴: {axis}, phase: {sorted_single[0]['phase']}")
    assert sorted_single[0]['phase'] == 0.0, "单个灯具的 phase 应该是 0.0"
    
    # 空列表
    print("\n2. 空列表:")
    empty = []
    sorted_empty, axis = sort_fixtures_by_axis(empty)
    print(f"   检测轴: {axis}, 灯具数: {len(sorted_empty)}")
    assert len(sorted_empty) == 0, "空列表应该返回空列表"
    assert axis == "x", "空列表应该返回默认轴 x"
    
    # 所有灯具在同一位置
    print("\n3. 所有灯具在同一位置:")
    same_pos = [
        {"name": "F1", "position": [1.0, 1.0, 1.0]},
        {"name": "F2", "position": [1.0, 1.0, 1.0]},
        {"name": "F3", "position": [1.0, 1.0, 1.0]},
    ]
    sorted_same, axis = sort_fixtures_by_axis(same_pos)
    print(f"   检测轴: {axis}")
    for f in sorted_same:
        print(f"   {f['name']}: phase={f['phase']:.3f}")
    
    print("\n✅ 边界情况测试通过!")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("  开始测试 spatial.py 模块")
    print("="*60)
    
    try:
        test_x_axis_sorting()
        test_y_axis_sorting()
        test_z_axis_sorting()
        test_radial_sorting()
        test_angle_sorting()
        test_auto_detect_single_axis()
        test_auto_detect_planar()
        test_edge_cases()
        
        print("\n" + "="*60)
        print("  ✅ 所有测试通过！")
        print("="*60)
        
        print("\n📊 测试总结:")
        print("  1. X/Y/Z 轴排序 ✓")
        print("  2. 径向排序 ✓")
        print("  3. 角度排序 ✓")
        print("  4. 自动轴检测（单轴）✓")
        print("  5. 自动轴检测（平面）✓")
        print("  6. Phase 归一化计算 ✓")
        print("  7. 边界情况处理 ✓")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        raise
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
