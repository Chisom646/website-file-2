-- Migration: Add language preference column to users table
-- Date: 2025-12-30
-- Description: Add language field to support i18n (en, yo, ha, ig)

-- Add language column with default value 'en'
ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR(2) DEFAULT 'en' NOT NULL;

-- Create index for faster language-based queries (optional, for future use)
CREATE INDEX IF NOT EXISTS idx_users_language ON users(language);
