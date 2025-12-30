-- Migration: Create communities, community_members, and chat_messages tables
-- Date: 2025-12-30
-- Description: Add tables for community/support group functionality with real-time chat

-- Create communities table
CREATE TABLE IF NOT EXISTS communities (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_by VARCHAR REFERENCES users(id),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_communities_name ON communities(name);

-- Create community_members table (join table)
CREATE TABLE IF NOT EXISTS community_members (
    id VARCHAR PRIMARY KEY,
    community_id VARCHAR NOT NULL REFERENCES communities(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    UNIQUE(community_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_community_members_community ON community_members(community_id);
CREATE INDEX IF NOT EXISTS idx_community_members_user ON community_members(user_id);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id VARCHAR PRIMARY KEY,
    community_id VARCHAR NOT NULL REFERENCES communities(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL REFERENCES users(id),
    message VARCHAR NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_community ON chat_messages(community_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at DESC);
