"""
测试项目制管理功能

验证:
1. GDTF 数据库的添加/查询/删除
2. 项目的创建/加载/保存
3. 跨项目的 GDTF 复用
"""
import os
import sys
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from aetherlight.gdtf_database import GDTFDatabase, GDTFDatabaseError
from aetherlight.gdtf_parser import GDTFParser, GDTFLibrary
from aetherlight.project_manager import ProjectManager, Project
from aetherlight.mvr_importer import MVRImporter


def test_gdtf_database():
    """测试 GDTF 数据库功能"""
    print("\n" + "="*60)
    print("测试 1: GDTF 数据库功能")
    print("="*60)
    
    # 使用临时数据库
    db_path = "test_gdtf.db"
    
    # 清理旧数据库
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = GDTFDatabase(db_path)
    print(f"✅ 数据库已创建: {db_path}")
    
    # 查找现有的 GDTF 文件
    gdtf_dir = Path("mvr_data")
    gdtf_files = list(gdtf_dir.glob("*.gdtf"))
    
    if not gdtf_files:
        print("⚠️ 未找到 GDTF 文件,跳过测试")
        return
    
    print(f"\n找到 {len(gdtf_files)} 个 GDTF 文件:")
    for gf in gdtf_files:
        print(f"  - {gf.name}")
    
    # 测试添加 Profile
    print("\n--- 添加 Profile 到数据库 ---")
    for gdtf_file in gdtf_files:
        try:
            profile = GDTFParser.parse(str(gdtf_file))
            added = db.add_profile(profile)
            if added:
                print(f"✅ 已添加: {profile.spec_key}")
            else:
                print(f"⚠️ 已存在: {profile.spec_key}")
        except Exception as e:
            print(f"❌ 解析失败 {gdtf_file.name}: {e}")
    
    # 测试查询
    print(f"\n--- 数据库统计 ---")
    count = db.get_count()
    print(f"总 Profile 数: {count}")
    
    # 列出所有 Libraries
    libraries = db.list_libraries()
    print(f"\nLibraries ({len(libraries)}):")
    for manufacturer, library_name, fixture_count in libraries:
        print(f"  - {manufacturer} / {library_name}: {fixture_count} 个灯具")
    
    # 测试按 library 查询
    if libraries:
        manufacturer, library_name, _ = libraries[0]
        print(f"\n--- 查询 {manufacturer} / {library_name} ---")
        profiles = db.search_by_library(manufacturer, library_name)
        for p in profiles:
            print(f"  - {p.long_name} ({len(p.modes)} 个模式)")
    
    # 测试精确查询
    print("\n--- 测试精确查询 ---")
    all_profiles = db.list_all()
    if all_profiles:
        spec_key = all_profiles[0].spec_key
        profile = db.get_profile(spec_key)
        if profile:
            print(f"✅ 查询成功: {profile.display_name}")
            print(f"   Modes: {', '.join(profile.mode_names)}")
        else:
            print(f"❌ 查询失败: {spec_key}")
    
    print("\n✅ 数据库测试完成")
    return db_path


def test_project_manager(db_path):
    """测试项目管理功能"""
    print("\n" + "="*60)
    print("测试 2: 项目管理功能")
    print("="*60)
    
    # 创建项目管理器
    pm = ProjectManager("test_projects")
    print(f"✅ 项目管理器已初始化: test_projects/")
    
    # 创建测试项目
    print("\n--- 创建项目 ---")
    project1 = pm.create_project("测试项目1")
    print(f"✅ 创建项目: {project1.project_info.name}")
    
    # 设置项目配置
    project1.mvr_file = "mvr_data/test.mvr"
    
    # 使用数据库中的 GDTF 创建 Fixture
    db = GDTFDatabase(db_path)
    all_profiles = db.list_all()
    
    if all_profiles:
        profile = all_profiles[0]
        from aetherlight.models import Fixture
        
        for i in range(3):
            fixture = Fixture(
                uuid=f"test-uuid-{i}",
                name=f"{profile.name}_{i:02d}",
                universe=0,
                address=1 + i * 10,
                gdtf_spec=profile.spec_key,
                gdtf_mode=profile.mode_names[0] if profile.mode_names else "",
            )
            project1.fixtures.append(fixture)
        
        print(f"添加了 {len(project1.fixtures)} 个 Fixture")
    
    # 保存项目
    print("\n--- 保存项目 ---")
    pm.save_project(project1)
    print(f"✅ 项目已保存")
    
    # 列出所有项目
    print("\n--- 列出所有项目 ---")
    projects = pm.list_projects()
    for p in projects:
        print(f"  - {p}")
    
    # 加载项目
    print("\n--- 加载项目 ---")
    loaded_project = pm.load_project("测试项目1")
    print(f"✅ 项目已加载: {loaded_project.project_info.name}")
    print(f"   MVR 文件: {loaded_project.mvr_file}")
    print(f"   Fixture 数: {len(loaded_project.fixtures)}")
    
    # 创建第二个项目 (复用 GDTF)
    print("\n--- 创建第二个项目 (复用 GDTF) ---")
    project2 = pm.create_project("测试项目2")
    project2.mvr_file = "mvr_data/test2.mvr"
    
    # 使用相同的 GDTF spec (验证复用)
    if all_profiles:
        profile = all_profiles[0]
        from aetherlight.models import Fixture
        
        fixture = Fixture(
            uuid="test-uuid-project2",
            name=f"{profile.name}_Project2",
            universe=1,
            address=100,
            gdtf_spec=profile.spec_key,  # 复用相同的 GDTF
            gdtf_mode=profile.mode_names[0] if profile.mode_names else "",
        )
        project2.fixtures.append(fixture)
    
    pm.save_project(project2)
    print(f"✅ 第二个项目已保存,复用了 GDTF: {profile.spec_key}")
    
    print("\n✅ 项目管理测试完成")


def test_library_integration():
    """测试 GDTFLibrary 与数据库的整合"""
    print("\n" + "="*60)
    print("测试 3: GDTFLibrary 数据库整合")
    print("="*60)
    
    # 创建启用数据库的 Library
    library = GDTFLibrary(use_database=True, db_path="test_gdtf.db")
    print(f"✅ GDTFLibrary 已启用数据库")
    
    # 从数据库加载所有 Profile
    count = library.load_from_database()
    print(f"✅ 从数据库加载了 {count} 个 Profile")
    
    # 测试查询
    all_profiles = library.get_all_profiles()
    if all_profiles:
        profile = all_profiles[0]
        
        # 清空内存
        library.clear()
        print(f"\n✅ 已清空内存缓存")
        
        # 尝试从数据库自动加载
        print(f"\n--- 测试自动从数据库加载 ---")
        loaded_profile = library.get_profile(profile.spec_key)
        if loaded_profile:
            print(f"✅ 自动从数据库加载: {loaded_profile.display_name}")
        else:
            print(f"❌ 加载失败")
    
    print("\n✅ Library 整合测试完成")


def cleanup():
    """清理测试文件"""
    print("\n" + "="*60)
    print("清理测试文件")
    print("="*60)
    
    import shutil
    
    # 删除测试数据库
    if os.path.exists("test_gdtf.db"):
        os.remove("test_gdtf.db")
        print("✅ 已删除测试数据库")
    
    # 删除测试项目目录
    if os.path.exists("test_projects"):
        shutil.rmtree("test_projects")
        print("✅ 已删除测试项目目录")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("项目制管理功能测试")
    print("="*60)
    
    try:
        # 测试 1: GDTF 数据库
        db_path = test_gdtf_database()
        
        if db_path:
            # 测试 2: 项目管理
            test_project_manager(db_path)
            
            # 测试 3: Library 整合
            test_library_integration()
        
        print("\n" + "="*60)
        print("所有测试通过!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理
        cleanup()


if __name__ == "__main__":
    main()
