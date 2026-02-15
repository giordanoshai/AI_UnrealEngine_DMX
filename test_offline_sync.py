# test_offline_sync.py
"""
测试离线缓存和同步功能
演示认证、离线操作和云端同步
"""
import sys
import time

# 导入数据库模块
from aetherlight.database.database import (
    set_offline_mode, is_offline_mode,
    create_effect, get_effect, list_effects, update_effect, delete_effect
)
from aetherlight.database.auth_manager import get_auth_manager
from aetherlight.database.sync_manager import get_sync_manager


def test_auth():
    """测试认证功能"""
    print("\n" + "="*80)
    print("测试 1: 用户认证")
    print("="*80)
    
    auth = get_auth_manager()
    
    # 检查当前认证状态
    if auth.is_authenticated():
        user = auth.get_current_user()
        print(f"✅ 已登录: {user.get('email') if user else 'Unknown'}")
    else:
        print("ℹ️  未登录，使用默认用户 ID")
    
    print(f"   当前用户 ID: {auth.get_current_user_id()}")


def test_offline_create():
    """测试离线创建"""
    print("\n" + "="*80)
    print("测试 2: 离线创建 Effect")
    print("="*80)
    
    # 切换到离线模式
    set_offline_mode(True)
    print(f"   离线模式: {is_offline_mode()}")
    
    # 创建测试 effect
    effect = create_effect(
        effect_name="离线测试效果",
        description="这是一个离线创建的测试效果",
        primitives=[
            {
                "type": "position",
                "targets": "all",
                "animation": "circle",
                "radius": 5000,
                "duration": 10.0
            }
        ],
        duration=10.0
    )
    
    if effect:
        print(f"✅ 离线创建成功!")
        print(f"   ID: {effect['id']}")
        print(f"   同步状态: {effect.get('sync_status')}")
        return effect['id']
    else:
        print("❌ 离线创建失败")
        return None


def test_offline_list():
    """测试离线列表"""
    print("\n" + "="*80)
    print("测试 3: 离线列出 Effects")
    print("="*80)
    
    effects = list_effects()
    print(f"   共 {len(effects)} 个 effect (离线缓存)")
    
    for i, effect in enumerate(effects[:3], 1):
        print(f"   {i}. {effect['effect_name']} ({effect.get('sync_status')})")


def test_sync_to_cloud(effect_id):
    """测试同步到云端"""
    print("\n" + "="*80)
    print("测试 4: 同步到云端")
    print("="*80)
    
    # 切换到在线模式
    set_offline_mode(False)
    
    # 执行同步
    sync = get_sync_manager()
    result = sync.sync_all()
    
    print(f"   上传: {result['uploaded']}")
    print(f"   下载: {result['downloaded']}")
    print(f"   冲突: {result['conflicts']}")
    print(f"   错误: {result['errors']}")


def test_online_operations():
    """测试在线操作"""
    print("\n" + "="*80)
    print("测试 5: 在线操作")
    print("="*80)
    
    # 确保在线模式
    set_offline_mode(False)
    
    # 列出云端 effects
    effects = list_effects()
    print(f"   云端共 {len(effects)} 个 effect")
    
    for i, effect in enumerate(effects[:3], 1):
        print(f"   {i}. {effect['effect_name']}")


def test_offline_update():
    """测试离线更新"""
    print("\n" + "="*80)
    print("测试 6: 离线更新 Effect")
    print("="*80)
    
    # 切换到离线模式
    set_offline_mode(True)
    
    # 获取第一个 effect
    effects = list_effects()
    if not effects:
        print("   ℹ️  本地缓存无 effect，跳过测试")
        return None
    
    effect_id = effects[0]['id']
    print(f"   更新 effect: {effects[0]['effect_name']}")
    
    # 更新
    updated = update_effect(
        effect_id,
        description="离线模式下更新的描述"
    )
    
    if updated:
        print(f"✅ 离线更新成功")
        print(f"   同步状态: {updated.get('sync_status')}")
        return effect_id
    else:
        print("❌ 离线更新失败")
        return None


def main():
    """主测试流程"""
    print("\n" + "="*80)
    print("         离线缓存与同步系统测试")
    print("="*80)
    
    try:
        # 1. 测试认证
        test_auth()
        
        # 2. 离线创建
        effect_id = test_offline_create()
        
        # 3. 离线列表
        test_offline_list()
        
        # 4. 同步到云端
        if effect_id:
            test_sync_to_cloud(effect_id)
        
        # 5. 在线操作
        test_online_operations()
        
        # 6. 离线更新
        updated_id = test_offline_update()
        
        # 7. 再次同步
        if updated_id:
            print("\n" + "="*80)
            print("测试 7: 再次同步")
            print("="*80)
            set_offline_mode(False)
            sync = get_sync_manager()
            result = sync.sync_all()
            print(f"   上传: {result['uploaded']}")
        
        print("\n" + "="*80)
        print("✅ 所有测试完成!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
