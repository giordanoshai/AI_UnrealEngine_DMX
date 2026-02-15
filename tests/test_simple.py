"""简化测试 - 验证核心功能"""
import sys
import os
import shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 测试前清理
if os.path.exists("test.db"):
    os.remove("test.db")
if os.path.exists("test_projects"):
    shutil.rmtree("test_projects")

# 测试 GDTF 数据库
print("="*50)
print("测试 GDTF 数据库")
print("="*50)

from aetherlight.gdtf_database import GDTFDatabase
from aetherlight.gdtf_parser import GDTFParser, GDTFLibrary

db = GDTFDatabase("test.db")
print("OK: 数据库创建成功")

# 解析GDTF文件
gdtf_files = list(Path("mvr_data").glob("*.gdtf"))
print(f"找到 {len(gdtf_files)} 个 GDTF 文件")

for gf in gdtf_files[:2]:  # 只测试前2个
    profile = GDTFParser.parse(str(gf))
    db.add_profile(profile)
    print(f"OK: 添加 {profile.spec_key}")

# 查询测试
count = db.get_count()
print(f"OK: 数据库中有 {count} 个 Profile")

# 测试 library_name 解析
libs = db.list_libraries()
for manufacturer, lib_name, count in libs:
    print(f"OK: Library {manufacturer}/{lib_name} 有 {count} 个灯具")

# 测试 Library 整合
print("\n" + "="*50)
print("测试 GDTFLibrary 数据库整合")
print("="*50)

lib = GDTFLibrary(use_database=True, db_path="test.db")
loaded = lib.load_from_database()
print(f"OK: 从数据库加载 {loaded} 个 Profile")

# 测试项目管理
print("\n" + "="*50)
print("测试项目管理")
print("="*50)

from aetherlight.project_manager import ProjectManager

pm = ProjectManager("test_projects")
project = pm.create_project("测试项目")
project.mvr_file = "test.mvr"
pm.save_project(project)
print(f"OK: 项目已保存")

loaded_proj = pm.load_project("测试项目")
print(f"OK: 项目已加载: {loaded_proj.project_info.name}")

# 清理
print("\n清理测试文件...")
del db  # 释放数据库连接
del lib  # 释放库引用
import time
time.sleep(0.1)  # 等待文件句柄释放

try:
    if os.path.exists("test.db"):
        os.remove("test.db")
        print("OK: 数据库已删除")
except Exception as e:
    print(f"警告: 无法删除数据库: {e}")

try:
    if os.path.exists("test_projects"):
        shutil.rmtree("test_projects")
        print("OK: 项目目录已删除")
except Exception as e:
    print(f"警告: 无法删除项目目录: {e}")

print("\n" + "="*50)
print("所有测试通过!")
print("="*50)
