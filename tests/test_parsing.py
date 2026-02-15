"""
AetherLight Pro — GDTF 解析 & MVR 导入 验证脚本

用法:
    .venv\\Scripts\\python.exe tests/test_parsing.py
"""
import logging
import os
import sys

# 确保可以导入 aetherlight 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aetherlight.gdtf_parser import GDTFParser, GDTFLibrary, GDTFParseError
from aetherlight.mvr_importer import MVRImporter, MVRParseError
from aetherlight.models import Fixture

# 日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("test")

# 数据路径
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "mvr_data",
)
GDTF_ROTAHEAD = os.path.join(
    DATA_DIR, "EpicGames@UE5_6_Generated_RotaHead@12_02_26.gdtf"
)
GDTF_ENTITY = os.path.join(
    DATA_DIR, "EpicGames@UE5_6_Generated_DMXEntityFixtureType@12_02_26.gdtf"
)
MVR_FILE = os.path.join(DATA_DIR, "GeneralSceneDescription.xml")

passed = 0
failed = 0


def check(condition: bool, description: str) -> None:
    global passed, failed
    if condition:
        print(f"  ✅ PASS: {description}")
        passed += 1
    else:
        print(f"  ❌ FAIL: {description}")
        failed += 1


def test_gdtf_parser():
    """Test 1: GDTF 解析器"""
    print("\n" + "=" * 60)
    print("TEST 1: GDTF Parser")
    print("=" * 60)

    # --- RotaHead ---
    print("\n--- RotaHead GDTF ---")
    profile = GDTFParser.parse(GDTF_ROTAHEAD)

    check(profile.name == "RotaHead", f"Name = '{profile.name}' (expected 'RotaHead')")
    check(profile.manufacturer == "Epic Games", f"Manufacturer = '{profile.manufacturer}'")
    check(
        profile.spec_key == "EpicGames@UE5_6_Generated_RotaHead@12_02_26",
        f"spec_key = '{profile.spec_key}'"
    )
    check("Mode" in profile.modes, f"Mode 'Mode' exists (modes: {list(profile.modes.keys())})")

    mode = profile.modes.get("Mode", {})
    check(len(mode) == 8, f"Channel count = {len(mode)} (expected 8)")
    check(mode.get("Pan") == 1, f"Pan offset = {mode.get('Pan')} (expected 1)")
    check(mode.get("Tilt") == 2, f"Tilt offset = {mode.get('Tilt')} (expected 2)")
    check(mode.get("Dimmer") == 5, f"Dimmer offset = {mode.get('Dimmer')} (expected 5)")
    check(mode.get("Shutter") == 6, f"Shutter offset = {mode.get('Shutter')} (expected 6)")
    check(mode.get("Frost") == 8, f"Frost offset = {mode.get('Frost')} (expected 8)")

    print(f"\n  Profile repr: {profile}")
    print(f"  Channel map: {mode}")

    # --- DMXEntityFixtureType ---
    print("\n--- DMXEntityFixtureType GDTF ---")
    profile2 = GDTFParser.parse(GDTF_ENTITY)

    check(profile2.name == "DMXEntityFixtureType", f"Name = '{profile2.name}'")
    mode2 = profile2.modes.get("Mode", {})
    check(len(mode2) == 1, f"Channel count = {len(mode2)} (expected 1)")
    check(mode2.get("Color") == 1, f"Color offset = {mode2.get('Color')} (expected 1)")


def test_mvr_importer():
    """Test 2: MVR 导入器"""
    print("\n" + "=" * 60)
    print("TEST 2: MVR Importer")
    print("=" * 60)

    fixtures = MVRImporter.parse(MVR_FILE)
    check(len(fixtures) == 4, f"Fixture count = {len(fixtures)} (expected 4)")

    # RotaHead_Mid
    mid = next((f for f in fixtures if f.name == "RotaHead_Mid"), None)
    check(mid is not None, "RotaHead_Mid found")
    if mid:
        check(mid.address == 1, f"RotaHead_Mid address = {mid.address} (expected 1)")
        check(mid.universe == 0, f"RotaHead_Mid universe = {mid.universe} (expected 0)")
        check(
            mid.gdtf_spec == "EpicGames@UE5_6_Generated_RotaHead@12_02_26",
            f"RotaHead_Mid gdtf_spec correct"
        )
        check(mid.gdtf_mode == "Mode", f"RotaHead_Mid gdtf_mode = '{mid.gdtf_mode}'")

        # 位置检查
        x, y, z = mid.position
        check(abs(x - (-685.46)) < 1.0, f"Position X ≈ -685.46 (got {x:.2f})")
        check(abs(y - (-7872.41)) < 1.0, f"Position Y ≈ -7872.41 (got {y:.2f})")
        check(abs(z - 4701.68) < 1.0, f"Position Z ≈ 4701.68 (got {z:.2f})")

    # RotaHead_R
    r = next((f for f in fixtures if f.name == "RotaHead_R"), None)
    check(r is not None, "RotaHead_R found")
    if r:
        check(r.address == 17, f"RotaHead_R address = {r.address} (expected 17)")

    # DMXEntityFixtureType
    entity = next((f for f in fixtures if f.name == "DMXEntityFixtureType"), None)
    check(entity is not None, "DMXEntityFixtureType found")
    if entity:
        check(entity.address == 33, f"DMXEntityFixtureType address = {entity.address} (expected 33)")

    print("\n  Fixture list:")
    for f in fixtures:
        print(f"    {f}")


def test_linking():
    """Test 3: GDTF 自动链接"""
    print("\n" + "=" * 60)
    print("TEST 3: Auto-Linking")
    print("=" * 60)

    # 构建库
    library = GDTFLibrary()
    library.add_from_file(GDTF_ROTAHEAD)
    library.add_from_file(GDTF_ENTITY)
    check(library.count == 2, f"Library count = {library.count} (expected 2)")

    # 导入灯具
    fixtures = MVRImporter.parse(MVR_FILE)

    # 自动链接
    patched, unpatched = MVRImporter.link_fixtures(fixtures, library)

    check(len(patched) == 4, f"Patched count = {len(patched)} (expected 4)")
    check(len(unpatched) == 0, f"Unpatched count = {len(unpatched)} (expected 0)")

    # 验证每个灯具的链接
    for f in fixtures:
        check(f.is_patched, f"'{f.name}' is patched")
        check(f.gdtf_profile is not None, f"'{f.name}' has linked profile")

    # 验证 DMX 值计算
    print("\n--- DMX 值测试 ---")
    mid = next((f for f in fixtures if f.name == "RotaHead_Mid"), None)
    if mid:
        # 设置属性
        mid.current_attributes["Dimmer"] = 1.0
        mid.current_attributes["Pan"] = 0.5
        dmx = mid.get_dmx_values()

        # Dimmer: offset=5, address=1 → absolute=5, value=255
        check(dmx.get(5) == 255, f"Dimmer DMX = {dmx.get(5)} (expected 255)")
        # Pan: offset=1, address=1 → absolute=1, value=127
        check(dmx.get(1) == 127, f"Pan DMX = {dmx.get(1)} (expected 127)")

        print(f"  DMX values (Dimmer=1.0, Pan=0.5): {dmx}")


def test_error_handling():
    """Test 4: 错误处理"""
    print("\n" + "=" * 60)
    print("TEST 4: Error Handling")
    print("=" * 60)

    # 不存在的文件
    try:
        GDTFParser.parse("nonexistent.gdtf")
        check(False, "Should raise GDTFParseError for missing file")
    except GDTFParseError:
        check(True, "GDTFParseError raised for missing file")

    # 不存在的 MVR 文件
    try:
        MVRImporter.parse("nonexistent.xml")
        check(False, "Should raise MVRParseError for missing file")
    except MVRParseError:
        check(True, "MVRParseError raised for missing MVR file")

    # 库模糊查找
    library = GDTFLibrary()
    library.add_from_file(GDTF_ROTAHEAD)
    results = library.find_by_name("rota")
    check(len(results) == 1, f"Fuzzy search 'rota' found {len(results)} (expected 1)")
    results2 = library.find_by_name("nonexistent")
    check(len(results2) == 0, f"Fuzzy search 'nonexistent' found {len(results2)} (expected 0)")


if __name__ == "__main__":
    print("╔════════════════════════════════════════════════╗")
    print("║  AetherLight Pro — Parsing Verification Tests  ║")
    print("╚════════════════════════════════════════════════╝")

    test_gdtf_parser()
    test_mvr_importer()
    test_linking()
    test_error_handling()

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)
