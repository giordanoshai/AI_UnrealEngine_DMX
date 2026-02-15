# upload_effects_to_supabase.py
"""
将 effect_examples.py 中的效果上传到 Supabase
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from aetherlight.database.database import create_effect, list_effects
from effect_examples import (
    EFFECT_BLUE_WAVE,
    EFFECT_RED_PULSE,
    EFFECT_GREEN_SCAN,
    EFFECT_WHITE_STATIC,
    EFFECT_CIRCLE_ZOOM_GOBO,
    EFFECT_FLASH,
    EFFECT_BLACKOUT,
)


def upload_all_effects():
    """上传所有效果到 Supabase"""
    print("=" * 80)
    print("           上传 Effects 到 Supabase")
    print("=" * 80)
    
    effects = [
        EFFECT_BLUE_WAVE,
        EFFECT_RED_PULSE,
        EFFECT_GREEN_SCAN,
        EFFECT_WHITE_STATIC,
        EFFECT_CIRCLE_ZOOM_GOBO,
        EFFECT_FLASH,
        EFFECT_BLACKOUT,
    ]
    
    success_count = 0
    error_count = 0
    
    for effect in effects:
        effect_name = effect.get("effect_name", "Unknown")
        description = effect.get("description", "")
        primitives = effect.get("primitives", [])
        duration = effect.get("duration", 10.0)
        
        print(f"\n上传: {effect_name} ({duration}s)...")
        
        result = create_effect(
            effect_name=effect_name,
            description=description,
            primitives=primitives,
            duration=duration
        )
        
        if result:
            success_count += 1
            print(f"  ✅ 成功 (ID: {result['id']})")
        else:
            error_count += 1
            print(f"  ❌ 失败")
    
    print("\n" + "=" * 80)
    print(f"上传完成: 成功 {success_count} 个, 失败 {error_count} 个")
    print("=" * 80)


def list_uploaded_effects():
    """列出已上传的效果"""
    print("\n" + "=" * 80)
    print("           已上传的 Effects")
    print("=" * 80)
    
    effects = list_effects()
    
    if not effects:
        print("❌ 没有找到任何 effect")
        return
    
    print(f"\n共 {len(effects)} 个效果:\n")
    
    for i, effect in enumerate(effects, 1):
        print(f"{i}. {effect['effect_name']}")
        print(f"   ID: {effect['id']}")
        print(f"   描述: {effect['description']}")
        print(f"   时长: {effect['duration']}s")
        print(f"   创建时间: {effect['created_at']}")
        print()


if __name__ == "__main__":
    print("\n请选择操作:")
    print("1. 上传所有 effects 到 Supabase")
    print("2. 列出已上传的 effects")
    print("3. 上传并列出")
    print()
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == "1":
        upload_all_effects()
    elif choice == "2":
        list_uploaded_effects()
    elif choice == "3":
        upload_all_effects()
        list_uploaded_effects()
    else:
        print("❌ 无效选择")
