# Better Auth Migration Guide

## 📋 Overview

This guide walks you through migrating your Neon PostgreSQL database to support Better Auth authentication. The migration will create the necessary tables and migrate existing user data while maintaining compatibility with your current system.

## 🎯 What This Migration Does

### Tables Created
1. **`users`** - Store user account information for Better Auth
2. **`sessions`** - Store user session information for authentication state
3. **`accounts`** - Store OAuth provider account links (Google, GitHub, etc.)

### Data Migration
- Migrates existing `cms_users` data to the new `users` table (if exists)
- Creates backup of existing data before migration
- Adds security constraints and indexes
- Creates cleanup procedures for maintenance

### Security Features
- Email format validation
- Role-based access control
- Session token validation
- Foreign key constraints
- Automated cleanup procedures

## 🚀 Migration Methods

Choose one of the following methods to run the migration:

### Method 1: Python Script (Recommended)

```bash
# From the project root
cd /Users/erickluna/Cloud_Repo/lunaxcode-admin

# Run the migration script
python scripts/migrate_better_auth.py
```

**Advantages:**
- ✅ Automated error handling
- ✅ Data validation
- ✅ Progress logging
- ✅ Rollback support
- ✅ Environment detection

### Method 2: Direct SQL Execution

```bash
# Connect to your Neon database
psql "postgresql://username:password@host/database"

# Run the SQL migration
\i docs/better-auth-sql-migration.sql
```

**Advantages:**
- ✅ Direct database control
- ✅ Can be run in parts
- ✅ No Python dependencies

### Method 3: SQLAlchemy Integration

```python
# Import and run from your application
from app.database.better_auth_migration import run_better_auth_migration
import asyncio

# Run migration
asyncio.run(run_better_auth_migration())
```

## 📋 Pre-Migration Checklist

### 1. Environment Setup
- [ ] Neon PostgreSQL database is accessible
- [ ] `DATABASE_URL` environment variable is set
- [ ] Python virtual environment is activated
- [ ] All dependencies are installed

### 2. Database Backup
- [ ] Create full database backup
- [ ] Test backup restoration process
- [ ] Document current schema state

### 3. Environment Variables
```bash
# Required
DATABASE_URL=postgresql://username:password@host/database

# Optional (for OAuth)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 4. Access Verification
```bash
# Test database connection
python -c "
import asyncio
from app.database.postgres import db_manager

async def test():
    await db_manager.health_check()
    print('✅ Database connection successful')

asyncio.run(test())
"
```

## 🏃‍♂️ Migration Steps

### Step 1: Run Migration

```bash
# Navigate to project root
cd /Users/erickluna/Cloud_Repo/lunaxcode-admin

# Run migration script
python scripts/migrate_better_auth.py
```

### Step 2: Verify Migration

The script will automatically verify:
- ✅ All tables created successfully
- ✅ Indexes are in place
- ✅ Data migration completed
- ✅ Security constraints added

### Step 3: Test Authentication

```python
# Test user creation
from app.models.database import User, UserRole
from app.database.postgres import db_manager

async def test_user_creation():
    async with db_manager.get_session() as session:
        # Create test user
        user = User(
            name="Test User",
            email="test@example.com",
            emailVerified=True,
            role=UserRole.ADMIN
        )
        session.add(user)
        await session.commit()
        print(f"✅ Created user: {user.email}")

# Run test
import asyncio
asyncio.run(test_user_creation())
```

## 🔧 Post-Migration Tasks

### 1. Update Environment Variables

Add Better Auth configuration to your `.env` file:

```env
# Better Auth Configuration
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars
BETTER_AUTH_URL=https://lunaxcode.com
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
```

### 2. Configure OAuth Providers

#### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs

#### Authorized Redirect URIs
```
https://yourdomain.com/api/auth/callback/google
http://localhost:3000/api/auth/callback/google  # For development
```

### 3. Update Frontend Integration

Update your frontend to use Better Auth endpoints:

```typescript
// Better Auth client configuration
import { betterAuth } from "better-auth/client"

export const authClient = betterAuth({
  baseURL: "https://lunaxcode-admin-qkeluna8941-yv8g04xo.apn.leapcell.dev",
  plugins: [
    // Add plugins as needed
  ]
})
```

### 4. Set Up Cleanup Jobs

Schedule regular cleanup of expired sessions and tokens:

```sql
-- Run daily cleanup (can be scheduled via cron or your hosting provider)
SELECT cleanup_expired_sessions();
SELECT cleanup_expired_oauth_tokens();
```

## 🔍 Verification Queries

### Check Table Structure
```sql
-- Verify tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'sessions', 'accounts');
```

### Check Data Migration
```sql
-- Check user count and sample data
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN "emailVerified" = true THEN 1 END) as verified_users,
    COUNT(CASE WHEN role = 'admin' THEN 1 END) as admin_users
FROM users;
```

### Check Indexes
```sql
-- Verify indexes were created
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE tablename IN ('users', 'sessions', 'accounts')
ORDER BY tablename, indexname;
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Error: could not connect to server
```
**Solution:** Verify DATABASE_URL and network connectivity
```bash
# Test connection
psql "$DATABASE_URL" -c "SELECT 1;"
```

#### 2. Permission Denied
```bash
# Error: permission denied for relation
```
**Solution:** Ensure database user has CREATE privileges
```sql
GRANT CREATE ON DATABASE your_database TO your_user;
```

#### 3. Table Already Exists
```bash
# Error: relation "users" already exists
```
**Solution:** The migration script handles this automatically. If running SQL manually, add `IF NOT EXISTS`:
```sql
CREATE TABLE IF NOT EXISTS users (...);
```

#### 4. Duplicate Email Error
```bash
# Error: duplicate key value violates unique constraint
```
**Solution:** The migration handles this by adding prefixes to conflicting emails.

### Recovery Procedures

#### Rollback Migration
```sql
-- Drop Better Auth tables (CAUTION: This will delete all auth data)
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Restore from backup if needed
-- (depends on your backup method)
```

#### Restore from Backup
```sql
-- If cms_users_backup exists
INSERT INTO cms_users SELECT * FROM cms_users_backup;
```

## 📊 Performance Optimization

### Recommended Indexes (Already Created)
```sql
-- Users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email_verified ON users("emailVerified");

-- Sessions table  
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_user_id ON sessions("userId");
CREATE INDEX idx_sessions_expires_at ON sessions("expiresAt");

-- Accounts table
CREATE INDEX idx_accounts_user_id ON accounts("userId");
CREATE INDEX idx_accounts_provider_account ON accounts("providerId", "accountId");
```

### Cleanup Schedule
```bash
# Add to crontab for daily cleanup at 2 AM
0 2 * * * psql "$DATABASE_URL" -c "SELECT cleanup_expired_sessions();"
0 2 * * * psql "$DATABASE_URL" -c "SELECT cleanup_expired_oauth_tokens();"
```

## 📈 Monitoring

### Key Metrics to Monitor
- Active user count
- Session duration patterns  
- OAuth provider usage
- Failed authentication attempts
- Database performance

### Monitoring Queries
```sql
-- Active sessions
SELECT COUNT(*) as active_sessions 
FROM sessions 
WHERE "expiresAt" > NOW();

-- OAuth provider distribution
SELECT "providerId", COUNT(*) as user_count 
FROM accounts 
GROUP BY "providerId";

-- Recent user registrations
SELECT DATE(created_at) as date, COUNT(*) as new_users
FROM users 
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date;
```

## 🔐 Security Best Practices

### 1. Environment Variables
- Use strong, unique secrets (min 32 characters)
- Rotate secrets regularly
- Never commit secrets to version control

### 2. Database Security
- Use SSL/TLS connections
- Implement connection pooling
- Regular security updates

### 3. Session Management
- Set appropriate session expiration times
- Implement session cleanup procedures
- Monitor for suspicious activity

### 4. OAuth Security
- Validate redirect URIs
- Use HTTPS for all OAuth flows
- Implement proper CSRF protection

## 🆘 Support

### Getting Help
1. Check the [Better Auth Documentation](https://better-auth.com/docs)
2. Review the error logs in `/logs/app.log`
3. Verify environment configuration
4. Test with minimal examples

### Useful Commands
```bash
# Check application logs
tail -f logs/app.log

# Test database connection
python -c "from app.database.postgres import db_manager; import asyncio; asyncio.run(db_manager.health_check())"

# Check table structure
psql "$DATABASE_URL" -c "\d users"
```

---

**Last Updated:** January 2025  
**Version:** 1.0  
**Migration Script:** `scripts/migrate_better_auth.py`
