-- ========================================================
-- Supabase SQL: Create Fixture Profiles Table
-- ========================================================
-- 该表用于存储灯具的定义（Profile），支持 JSONB 格式的通道详细配置。
-- 结构参考自 fixture_config.py 中的 MOVE_HEAD 定义。

CREATE TABLE IF NOT EXISTS fixture_profiles (
    -- 基础标识
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fixture_id TEXT,                    -- 对应配置中的 UUID 字符串 (如 FD9E205E-...)
    name TEXT NOT NULL,                 -- 灯具名称 (如 DMXL_huzhou RotaHead)
    manufacturer TEXT,                  -- 制造商 (如 DMXL_huzhou)
    
    -- 核心配置 (JSONB)
    -- 存储 channels 字典，包含 offset, default_value, type, mapping 等所有细节
    channels JSONB NOT NULL DEFAULT '{}'::jsonb, 
    
    -- 其他元数据
    dmx_start_address INTEGER DEFAULT 1, -- 默认起始 DMX 地址
    file_path TEXT,                     -- 源文件路径 (如果是从 GDTF 导入的)
    user_id UUID,                       -- 所属用户 ID
    
    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 唯一性约束
    UNIQUE(manufacturer, name)
);

-- 添加常用查询索引
CREATE INDEX IF NOT EXISTS idx_fixture_profiles_name ON fixture_profiles(name);
CREATE INDEX IF NOT EXISTS idx_fixture_profiles_manufacturer ON fixture_profiles(manufacturer);

-- 自动更新 updated_at 的触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS tr_fixture_profiles_updated_at ON fixture_profiles;
CREATE TRIGGER tr_fixture_profiles_updated_at 
    BEFORE UPDATE ON fixture_profiles
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 注释说明
COMMENT ON TABLE fixture_profiles IS '存储灯具配置定义，channels 字段采用 JSONB 存储详细映射';
COMMENT ON COLUMN fixture_profiles.channels IS '包含通道偏移、默认值、类型及离散值映射的 JSON 对象';
