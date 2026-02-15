
import sys
import os

# Ensure we can import modules from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aetherlight.database.database import create_gdtf_profile, list_gdtf_profiles
from aetherlight.fixture_config import MOVE_HEAD

def migrate():
    print("🚀 Starting migration of fixture_config.py to Supabase...")
    
    # 1. Parse data from MOVE_HEAD
    full_name = MOVE_HEAD["name"] # "DMXL_huzhou RotaHead"
    parts = full_name.split(maxsplit=1)
    if len(parts) == 2:
        manufacturer = parts[0]
        name = parts[1]
    else:
        manufacturer = "Generic"
        name = full_name
        
    long_name = full_name
    mode_name = "Standard"
    
    # Calculate channel map and count
    channels = MOVE_HEAD["channels"]
    channel_map = {}
    max_offset = -1
    
    for ch_name, config in channels.items():
        # Store full config, but update offset to 1-based
        new_config = config.copy()
        new_config["offset"] = config["offset"] + 1
        channel_map[ch_name] = new_config
        max_offset = max(max_offset, new_config["offset"])
        
    channel_count = max_offset # max_offset is already 1-based count if contiguous?
    # If offsets are 1, 2, ... N. Max offset is N. Count is N.
    # config["offset"] 0 -> 1.
    
    # 3. Create in Database
    result = create_gdtf_profile(
        manufacturer=manufacturer,
        name=name,
        long_name=long_name,
        modes={mode_name: channel_map}
    )
    
    if result:
        print(f"✅ Successfully migrated {name} to database!")
    else:
        print(f"❌ Failed to migrate {name}.")

if __name__ == "__main__":
    migrate()
