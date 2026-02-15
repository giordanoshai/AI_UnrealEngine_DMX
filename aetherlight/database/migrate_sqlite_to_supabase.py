# aetherlight/database/migrate_sqlite_to_supabase.py
"""
SQLite 到 Supabase 数据迁移脚本
将 gdtf_library.db 中的数据迁移到 Supabase
"""
import sqlite3
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from aetherlight.database.database import get_supabase


def migrate_gdtf_profiles():
    """迁移 gdtf_profiles 表"""
    print("=" * 80)
    print("开始迁移 gdtf_profiles 表...")
    print("=" * 80)
    
    # 连接 SQLite
    sqlite_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'gdtf_library.db')
    if not os.path.exists(sqlite_db_path):
        print(f"❌ SQLite 数据库文件不存在: {sqlite_db_path}")
        return False
    
    conn = sqlite3.connect(sqlite_db_path)
    cursor = conn.cursor()
    
    # 读取所有数据
    try:
        cursor.execute("SELECT manufacturer, name, long_name, library_name, fixture_name, spec_key, file_path, created_at FROM gdtf_profiles")
        rows = cursor.fetchall()
        print(f"✅ 从 SQLite 读取到 {len(rows)} 条 gdtf_profiles 记录")
    except Exception as e:
        print(f"❌ 读取 SQLite 数据失败: {e}")
        conn.close()
        return False
    
    # 写入 Supabase
    supabase = get_supabase(service_role=True)
    success_count = 0
    error_count = 0
    
    for row in rows:
        manufacturer, name, long_name, library_name, fixture_name, spec_key, file_path, created_at = row
        
        data = {
            "manufacturer": manufacturer,
            "name": name,
            "long_name": long_name,
            "library_name": library_name,
            "fixture_name": fixture_name,
            "spec_key": spec_key,
            "file_path": file_path,
            # created_at 会使用数据库默认值
        }
        
        try:
            supabase.table("gdtf_profiles").insert(data).execute()
            success_count += 1
            print(f"✅ [{success_count}/{len(rows)}] {manufacturer} - {long_name}")
        except Exception as e:
            error_count += 1
            print(f"❌ 插入失败 ({spec_key}): {e}")
    
    conn.close()
    
    print(f"\n迁移完成: 成功 {success_count} 条, 失败 {error_count} 条")
    return error_count == 0


def migrate_gdtf_modes():
    """迁移 gdtf_modes 表"""
    print("\n" + "=" * 80)
    print("开始迁移 gdtf_modes 表...")
    print("=" * 80)
    
    # 连接 SQLite
    sqlite_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'gdtf_library.db')
    conn = sqlite3.connect(sqlite_db_path)
    cursor = conn.cursor()
    
    # 首先需要建立 profile_id 映射 (SQLite ID -> Supabase UUID)
    print("📋 建立 profile_id 映射...")
    
    supabase = get_supabase(service_role=True)
    
    # 获取 Supabase 中的所有 profiles
    supabase_profiles = supabase.table("gdtf_profiles").select("id, spec_key").execute()
    spec_key_to_uuid = {p["spec_key"]: p["id"] for p in supabase_profiles.data}
    
    # 读取 SQLite 中的 modes 数据
    try:
        cursor.execute("""
            SELECT m.profile_id, m.mode_name, m.channel_map, m.channel_count, p.spec_key
            FROM gdtf_modes m
            JOIN gdtf_profiles p ON m.profile_id = p.id
        """)
        rows = cursor.fetchall()
        print(f"✅ 从 SQLite 读取到 {len(rows)} 条 gdtf_modes 记录")
    except Exception as e:
        print(f"❌ 读取 SQLite 数据失败: {e}")
        conn.close()
        return False
    
    # 写入 Supabase
    success_count = 0
    error_count = 0
    
    for row in rows:
        sqlite_profile_id, mode_name, channel_map, channel_count, spec_key = row
        
        # 查找对应的 Supabase UUID
        supabase_profile_uuid = spec_key_to_uuid.get(spec_key)
        if not supabase_profile_uuid:
            print(f"❌ 找不到对应的 profile: {spec_key}")
            error_count += 1
            continue
        
        data = {
            "profile_id": supabase_profile_uuid,
            "mode_name": mode_name,
            "channel_map": channel_map,
            "channel_count": channel_count,
        }
        
        try:
            supabase.table("gdtf_modes").insert(data).execute()
            success_count += 1
            print(f"✅ [{success_count}/{len(rows)}] {spec_key} - {mode_name}")
        except Exception as e:
            error_count += 1
            print(f"❌ 插入失败: {e}")
    
    conn.close()
    
    print(f"\n迁移完成: 成功 {success_count} 条, 失败 {error_count} 条")
    return error_count == 0


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("           SQLite → Supabase 数据迁移工具")
    print("=" * 80)
    print("\n⚠️  警告: 此操作将把 gdtf_library.db 的数据迁移到 Supabase")
    print("   请确保 Supabase 表已经创建(运行 create_tables.sql)")
    print("\n是否继续? (y/n): ", end='')
    
    confirm = input().strip().lower()
    if confirm != 'y':
        print("❌ 用户取消操作")
        return
    
    # 迁移 profiles
    if not migrate_gdtf_profiles():
        print("\n❌ gdtf_profiles 迁移失败,停止迁移")
        return
    
    # 迁移 modes
    if not migrate_gdtf_modes():
        print("\n❌ gdtf_modes 迁移失败")
        return
    
    print("\n" + "=" * 80)
    print("           ✅ 所有数据迁移完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
