-- ============================================================================
-- Better Auth Database Migration for Neon PostgreSQL
-- ============================================================================
-- 
-- This SQL script creates the required tables for Better Auth integration.
-- Based on the schema defined in docs/better-auth-database-schema.md
--
-- Tables created:
-- 1. users - Store user account information
-- 2. sessions - Store user session information  
-- 3. accounts - Store OAuth provider account links
--
-- ============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    "emailVerified" BOOLEAN DEFAULT FALSE,
    image VARCHAR(255),
    role VARCHAR(50) DEFAULT 'admin' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_email_verified ON users("emailVerified");
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Add constraints for users table
ALTER TABLE users 
ADD CONSTRAINT IF NOT EXISTS chk_email_format 
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE users
ADD CONSTRAINT IF NOT EXISTS chk_role_values
CHECK (role IN ('admin', 'super_admin', 'user'));

-- ============================================================================
-- 2. SESSIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    "userId" VARCHAR(255) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    "expiresAt" TIMESTAMP WITH TIME ZONE NOT NULL,
    "ipAddress" VARCHAR(45),
    "userAgent" TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for sessions table
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions("userId");
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions("expiresAt");
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);

-- Add constraints for sessions table
ALTER TABLE sessions
ADD CONSTRAINT IF NOT EXISTS chk_token_length
CHECK (LENGTH(token) >= 32);

-- Add foreign key constraint for sessions
ALTER TABLE sessions
ADD CONSTRAINT IF NOT EXISTS fk_sessions_user
FOREIGN KEY ("userId") REFERENCES users(id) ON DELETE CASCADE;

-- ============================================================================
-- 3. ACCOUNTS TABLE (OAuth Providers)
-- ============================================================================

CREATE TABLE IF NOT EXISTS accounts (
    id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    "userId" VARCHAR(255) NOT NULL,
    "providerId" VARCHAR(50) NOT NULL,
    "accountId" VARCHAR(255) NOT NULL,
    "accessToken" TEXT,
    "refreshToken" TEXT,
    "expiresAt" TIMESTAMP WITH TIME ZONE,
    scope TEXT,
    "tokenType" VARCHAR(50) DEFAULT 'bearer' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for accounts table
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts("userId");
CREATE INDEX IF NOT EXISTS idx_accounts_provider_id ON accounts("providerId");
CREATE INDEX IF NOT EXISTS idx_accounts_provider_account ON accounts("providerId", "accountId");
CREATE INDEX IF NOT EXISTS idx_accounts_expires_at ON accounts("expiresAt");

-- Add constraints for accounts table
ALTER TABLE accounts
ADD CONSTRAINT IF NOT EXISTS chk_provider_values
CHECK ("providerId" IN ('google', 'github', 'microsoft', 'apple'));

-- Add unique constraint for provider accounts
ALTER TABLE accounts
ADD CONSTRAINT IF NOT EXISTS unique_provider_account 
UNIQUE ("providerId", "accountId");

-- Add foreign key constraint for accounts
ALTER TABLE accounts
ADD CONSTRAINT IF NOT EXISTS fk_accounts_user
FOREIGN KEY ("userId") REFERENCES users(id) ON DELETE CASCADE;

-- ============================================================================
-- 4. DATA MIGRATION FROM cms_users (if exists)
-- ============================================================================

-- Check if cms_users table exists and migrate data
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'cms_users') THEN
        -- Create backup first
        CREATE TABLE IF NOT EXISTS cms_users_backup AS SELECT * FROM cms_users;
        
        -- Migrate active users with valid emails
        INSERT INTO users (id, name, email, "emailVerified", role, created_at, updated_at)
        SELECT 
            CONCAT('cms_', id::text) as id,
            username as name,
            email,
            TRUE as "emailVerified",
            'admin' as role,
            created_at,
            updated_at
        FROM cms_users
        WHERE is_active = TRUE 
        AND email IS NOT NULL 
        AND email != ''
        AND email NOT IN (SELECT email FROM users)  -- Avoid duplicates
        ON CONFLICT (email) DO NOTHING;  -- Skip if email already exists
        
        RAISE NOTICE 'Migrated cms_users data to users table';
    ELSE
        RAISE NOTICE 'No cms_users table found, skipping migration';
    END IF;
END $$;

-- ============================================================================
-- 5. SAMPLE DATA (Optional - only if no users exist)
-- ============================================================================

-- Insert sample admin user if no users exist
INSERT INTO users (id, name, email, "emailVerified", role) 
SELECT 'admin_001', 'Admin User', 'admin@lunaxcode.com', TRUE, 'admin'
WHERE NOT EXISTS (SELECT 1 FROM users);

-- ============================================================================
-- 6. CLEANUP FUNCTIONS
-- ============================================================================

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sessions 
    WHERE "expiresAt" < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired OAuth tokens
CREATE OR REPLACE FUNCTION cleanup_expired_oauth_tokens()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE accounts 
    SET "accessToken" = NULL, "refreshToken" = NULL 
    WHERE "expiresAt" < NOW();
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ============================================================================

-- Function for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_sessions_updated_at 
    BEFORE UPDATE ON sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_accounts_updated_at 
    BEFORE UPDATE ON accounts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 8. VERIFICATION QUERIES
-- ============================================================================

-- Verify tables were created
SELECT 
    schemaname, 
    tablename, 
    tableowner 
FROM pg_tables 
WHERE tablename IN ('users', 'sessions', 'accounts')
ORDER BY tablename;

-- Check indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename IN ('users', 'sessions', 'accounts')
ORDER BY tablename, indexname;

-- Check user count
SELECT 
    'users' as table_name,
    COUNT(*) as record_count
FROM users
UNION ALL
SELECT 
    'sessions' as table_name,
    COUNT(*) as record_count
FROM sessions
UNION ALL
SELECT 
    'accounts' as table_name,
    COUNT(*) as record_count
FROM accounts;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Display completion message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE '✅ Better Auth migration completed successfully!';
    RAISE NOTICE '';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - users: Store user account information';
    RAISE NOTICE '  - sessions: Store user session information';
    RAISE NOTICE '  - accounts: Store OAuth provider account links';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Update your frontend to use Better Auth';
    RAISE NOTICE '  2. Configure OAuth providers (Google, GitHub, etc.)';
    RAISE NOTICE '  3. Test authentication flow';
    RAISE NOTICE '  4. Set up automated cleanup jobs for expired sessions';
    RAISE NOTICE '';
    RAISE NOTICE 'Cleanup functions available:';
    RAISE NOTICE '  - SELECT cleanup_expired_sessions();';
    RAISE NOTICE '  - SELECT cleanup_expired_oauth_tokens();';
    RAISE NOTICE '============================================================================';
END $$;
