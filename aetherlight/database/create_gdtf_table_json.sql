-- Create gdtf_profiles table with JSONB modes storage
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS gdtf_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    manufacturer TEXT NOT NULL,
    name TEXT NOT NULL,
    long_name TEXT NOT NULL,
    modes JSONB NOT NULL DEFAULT '{}'::jsonb,  -- Stores {mode_name: channel_map}
    file_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID,
    UNIQUE(manufacturer, long_name)
);

CREATE INDEX IF NOT EXISTS idx_gdtf_profiles_name ON gdtf_profiles(name);
CREATE INDEX IF NOT EXISTS idx_gdtf_profiles_manufacturer ON gdtf_profiles(manufacturer);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_gdtf_profiles_updated_at ON gdtf_profiles;
CREATE TRIGGER update_gdtf_profiles_updated_at BEFORE UPDATE ON gdtf_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
