-- Supabase 数据库表结构
-- 创建时间: 2026-02-15

-- ========================================
-- Effects 表 - 存储灯光效果定义
-- ========================================
CREATE TABLE IF NOT EXISTS effects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    effect_name TEXT NOT NULL,
    description TEXT,
    primitives JSONB NOT NULL,  -- 动画定义数组
    duration FLOAT NOT NULL DEFAULT 10.0,  -- 持续时间(秒)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(effect_name)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_effects_name ON effects(effect_name);

-- 更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_effects_updated_at BEFORE UPDATE ON effects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ========================================
-- Projects 表 - 存储项目信息
-- ========================================
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name TEXT NOT NULL,
    fixtures JSONB NOT NULL,  -- 灯具配置数组
    channel_config JSONB,  -- 通道配置
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_name)
);

CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(project_name);

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ========================================
-- Cue Lists 表 - 存储 cue list 配置
-- ========================================
CREATE TABLE IF NOT EXISTS cue_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cue_list_name TEXT NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    cues JSONB NOT NULL,  -- cue 配置数组
    loop BOOLEAN DEFAULT FALSE,  -- 是否循环播放
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cue_lists_name ON cue_lists(cue_list_name);
CREATE INDEX IF NOT EXISTS idx_cue_lists_project ON cue_lists(project_id);

CREATE TRIGGER update_cue_lists_updated_at BEFORE UPDATE ON cue_lists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ========================================
-- GDTF Profiles 表 - 从 SQLite 迁移
-- ========================================
CREATE TABLE IF NOT EXISTS gdtf_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    manufacturer TEXT NOT NULL,
    name TEXT NOT NULL,
    long_name TEXT NOT NULL,
    library_name TEXT,
    fixture_name TEXT,
    spec_key TEXT UNIQUE NOT NULL,
    file_path TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(manufacturer, long_name)
);

CREATE INDEX IF NOT EXISTS idx_gdtf_profiles_library ON gdtf_profiles(manufacturer, library_name);
CREATE INDEX IF NOT EXISTS idx_gdtf_profiles_spec_key ON gdtf_profiles(spec_key);


-- ========================================
-- GDTF Modes 表 - 从 SQLite 迁移
-- ========================================
CREATE TABLE IF NOT EXISTS gdtf_modes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES gdtf_profiles(id) ON DELETE CASCADE,
    mode_name TEXT NOT NULL,
    channel_map TEXT NOT NULL,
    channel_count INTEGER NOT NULL,
    UNIQUE(profile_id, mode_name)
);

CREATE INDEX IF NOT EXISTS idx_gdtf_modes_profile ON gdtf_modes(profile_id);


-- ========================================
-- 启用 RLS (Row Level Security) - 可选
-- ========================================
-- 如果需要权限控制,可以启用以下代码

-- ALTER TABLE effects ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE cue_lists ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE gdtf_profiles ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE gdtf_modes ENABLE ROW LEVEL SECURITY;

-- 创建公开访问策略(开发环境)
-- CREATE POLICY "Enable read access for all users" ON effects FOR SELECT USING (true);
-- CREATE POLICY "Enable insert access for all users" ON effects FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Enable update access for all users" ON effects FOR UPDATE USING (true);
-- CREATE POLICY "Enable delete access for all users" ON effects FOR DELETE USING (true);

-- 其他表同理...
