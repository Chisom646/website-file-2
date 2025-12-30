# Database Migrations

This directory contains SQL migration files for the People Help The People database schema.

## Overview

Migrations are applied manually using `psql` or programmatically via the application. Each migration file is numbered sequentially and includes a descriptive name.

## Migration Files

### 001_add_language_to_users.sql
**Date**: 2025-12-30
**Purpose**: Add i18n language preference support

**Changes**:
- Adds `language` column to `users` table (VARCHAR(2), default 'en')
- Creates index on language column for future query optimization
- Supported languages: en (English), yo (Yoruba), ha (Hausa), ig (Igbo)

**Apply**:
```bash
psql -U your_db_user -d people_help_db -f people_help/migrations/001_add_language_to_users.sql
```

### 002_create_communities_tables.sql
**Date**: 2025-12-30
**Purpose**: Create community and chat functionality

**Changes**:
- Creates `communities` table for support groups
- Creates `community_members` table (many-to-many join)
- Creates `chat_messages` table for real-time chat
- Includes indexes for performance optimization
- Enforces unique constraint on (community_id, user_id) for membership

**Apply**:
```bash
psql -U your_db_user -d people_help_db -f people_help/migrations/002_create_communities_tables.sql
```

### 003_create_posts_table.sql
**Date**: 2025-12-30
**Purpose**: Create feed/posts functionality

**Changes**:
- Creates `posts` table for user-generated content
- Posts can be general or community-specific (optional community_id)
- Includes indexes on user_id, community_id, and created_at
- Supports cascading deletes for users and communities

**Apply**:
```bash
psql -U your_db_user -d people_help_db -f people_help/migrations/003_create_posts_table.sql
```

## How to Apply Migrations

### Method 1: Using psql (Recommended for manual application)

```bash
# Apply all migrations in order
psql -U your_db_user -d people_help_db -f people_help/migrations/001_add_language_to_users.sql
psql -U your_db_user -d people_help_db -f people_help/migrations/002_create_communities_tables.sql
psql -U your_db_user -d people_help_db -f people_help/migrations/003_create_posts_table.sql
```

### Method 2: Apply all at once

```bash
for file in people_help/migrations/*.sql; do
    echo "Applying migration: $file"
    psql -U your_db_user -d people_help_db -f "$file"
done
```

### Method 3: From application startup

The base tables are automatically created when the FastAPI application starts via SQLModel's `create_all()` method. However, the migration files provide additional schema changes and indexes that may not be covered by the ORM.

## Best Practices

1. **Never modify existing migration files** - Create a new migration instead
2. **Always use IF NOT EXISTS** clauses to make migrations idempotent
3. **Test migrations on a development database** before applying to production
4. **Keep migrations small and focused** - One logical change per file
5. **Document what each migration does** - Include date and description comments

## Database Connection

Ensure your `.env` file has the correct database credentials:

```env
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=people_help_db
```

## Schema Overview

After applying all migrations, the database includes:

**Core Tables**:
- `users` - User authentication and profile
- `person` - Extended user information
- `roles` - User role definitions
- `user_role` - User-role associations

**Feature Tables**:
- `communities` - Support groups/communities
- `community_members` - Community membership
- `chat_messages` - Real-time chat messages
- `posts` - User feed posts

## Rollback

These migrations do not include rollback scripts. To rollback:

1. **Drop tables** (data loss):
   ```sql
   DROP TABLE IF EXISTS posts CASCADE;
   DROP TABLE IF EXISTS chat_messages CASCADE;
   DROP TABLE IF EXISTS community_members CASCADE;
   DROP TABLE IF EXISTS communities CASCADE;
   ```

2. **Remove column** (for 001):
   ```sql
   ALTER TABLE users DROP COLUMN IF EXISTS language;
   ```

**Warning**: Rollbacks will result in data loss. Always backup your database before applying or rolling back migrations.
