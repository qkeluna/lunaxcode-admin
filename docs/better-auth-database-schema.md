# Better Auth Database Schema - External API Integration

## 📋 Overview

This document outlines the required database tables and schema changes needed to integrate Better Auth with the external API at `https://lunaxcode-admin-qkeluna8941-yv8g04xo.apn.leapcell.dev/api/v1/`.

**Current Setup:**
- External API handles all admin dashboard data
- Better Auth currently uses in-memory storage (needs migration)
- Existing `cms_users` table handles legacy authentication

**Goal:**
- Migrate Better Auth to use external API database
- Maintain existing admin functionality
- Support both email/password and Google OAuth authentication

---

## 🗃️ Required Database Tables

### 1. `users` Table

**Purpose:** Store user account information for Better Auth authentication.

```sql
CREATE TABLE users (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE NOT NULL,
  emailVerified BOOLEAN DEFAULT FALSE,
  image VARCHAR(255),
  role VARCHAR(50) DEFAULT 'admin',
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  -- Indexes for performance
  INDEX idx_users_email (email),
  INDEX idx_users_role (role),
  INDEX idx_users_created (createdAt)
);
```

**Field Descriptions:**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | VARCHAR(255) | PRIMARY KEY | Unique identifier for each user |
| `name` | VARCHAR(255) | NULL | User's display name |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email address for login |
| `emailVerified` | BOOLEAN | DEFAULT FALSE | Whether email is verified |
| `image` | VARCHAR(255) | NULL | Profile image URL (from Google OAuth) |
| `role` | VARCHAR(50) | DEFAULT 'admin' | User role (all users are admin) |
| `createdAt` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| `updatedAt` | TIMESTAMP | AUTO UPDATE | Last modification timestamp |

**Sample Data:**
```sql
INSERT INTO users (id, name, email, emailVerified, role) VALUES
('admin_001', 'Admin User', 'admin@lunaxcode.com', TRUE, 'admin'),
('user_002', 'John Doe', 'john@example.com', TRUE, 'admin');
```

---

### 2. `sessions` Table

**Purpose:** Store user session information for authentication state management.

```sql
CREATE TABLE sessions (
  id VARCHAR(255) PRIMARY KEY,
  userId VARCHAR(255) NOT NULL,
  token VARCHAR(255) UNIQUE NOT NULL,
  expiresAt TIMESTAMP NOT NULL,
  ipAddress VARCHAR(45),
  userAgent TEXT,
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  -- Foreign key relationship
  FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE,
  
  -- Indexes for performance
  INDEX idx_sessions_token (token),
  INDEX idx_sessions_user (userId),
  INDEX idx_sessions_expires (expiresAt)
);
```

**Field Descriptions:**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | VARCHAR(255) | PRIMARY KEY | Unique session identifier |
| `userId` | VARCHAR(255) | NOT NULL, FK | Reference to users table |
| `token` | VARCHAR(255) | UNIQUE, NOT NULL | Session token for authentication |
| `expiresAt` | TIMESTAMP | NOT NULL | Session expiration time |
| `ipAddress` | VARCHAR(45) | NULL | Client IP address (IPv4/IPv6) |
| `userAgent` | TEXT | NULL | Browser/client information |
| `createdAt` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Session creation time |
| `updatedAt` | TIMESTAMP | AUTO UPDATE | Last session update |

**Sample Data:**
```sql
INSERT INTO sessions (id, userId, token, expiresAt, ipAddress) VALUES
('sess_001', 'admin_001', 'tok_abc123xyz', '2024-02-01 12:00:00', '192.168.1.100');
```

---

### 3. `accounts` Table

**Purpose:** Store OAuth provider account links (Google, etc.) for social authentication.

```sql
CREATE TABLE accounts (
  id VARCHAR(255) PRIMARY KEY,
  userId VARCHAR(255) NOT NULL,
  providerId VARCHAR(50) NOT NULL,
  accountId VARCHAR(255) NOT NULL,
  accessToken TEXT,
  refreshToken TEXT,
  expiresAt TIMESTAMP,
  scope TEXT,
  tokenType VARCHAR(50) DEFAULT 'bearer',
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  -- Foreign key relationship
  FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE,
  
  -- Unique constraint for provider accounts
  UNIQUE KEY unique_provider_account (providerId, accountId),
  
  -- Indexes for performance
  INDEX idx_accounts_user (userId),
  INDEX idx_accounts_provider (providerId),
  INDEX idx_accounts_expires (expiresAt)
);
```

**Field Descriptions:**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | VARCHAR(255) | PRIMARY KEY | Unique account link identifier |
| `userId` | VARCHAR(255) | NOT NULL, FK | Reference to users table |
| `providerId` | VARCHAR(50) | NOT NULL | OAuth provider ('google', 'github', etc.) |
| `accountId` | VARCHAR(255) | NOT NULL | Provider-specific user ID |
| `accessToken` | TEXT | NULL | OAuth access token |
| `refreshToken` | TEXT | NULL | OAuth refresh token |
| `expiresAt` | TIMESTAMP | NULL | Token expiration time |
| `scope` | TEXT | NULL | OAuth permissions granted |
| `tokenType` | VARCHAR(50) | DEFAULT 'bearer' | Token type |
| `createdAt` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Link creation time |
| `updatedAt` | TIMESTAMP | AUTO UPDATE | Last update time |

**Sample Data:**
```sql
INSERT INTO accounts (id, userId, providerId, accountId, tokenType) VALUES
('acc_001', 'admin_001', 'google', '1234567890', 'bearer');
```

---

## 🔄 Data Migration

### Migration from `cms_users` to `users`

**Step 1: Backup existing data**
```sql
-- Create backup of cms_users table
CREATE TABLE cms_users_backup AS SELECT * FROM cms_users;
```

**Step 2: Migrate data to new users table**
```sql
-- Insert existing cms_users into the new users table
INSERT INTO users (id, name, email, emailVerified, role, createdAt, updatedAt)
SELECT 
  CONCAT('cms_', id) as id,           -- Prefix to avoid ID conflicts
  username as name,                   -- Map username to name
  email,                             -- Keep email as-is
  TRUE as emailVerified,             -- Existing users are verified
  'admin' as role,                   -- All users are admin
  created_at as createdAt,           -- Map timestamps
  updated_at as updatedAt
FROM cms_users
WHERE is_active = TRUE               -- Only migrate active users
  AND email IS NOT NULL             -- Ensure email exists
  AND email != '';                  -- Ensure email is not empty

-- Update any duplicate emails if needed
UPDATE users 
SET email = CONCAT(LEFT(email, LOCATE('@', email) - 1), '+', id, SUBSTRING(email, LOCATE('@', email)))
WHERE id IN (
  SELECT id FROM (
    SELECT id, ROW_NUMBER() OVER (PARTITION BY email ORDER BY createdAt) as rn
    FROM users
  ) t WHERE rn > 1
);
```

**Step 3: Verify migration**
```sql
-- Check migration results
SELECT 
  'cms_users' as source_table, COUNT(*) as count
FROM cms_users 
WHERE is_active = TRUE

UNION ALL

SELECT 
  'users' as source_table, COUNT(*) as count
FROM users;

-- Verify no duplicate emails
SELECT email, COUNT(*) as count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

---

## 📊 Database Indexes and Performance

### Recommended Indexes

```sql
-- Users table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created ON users(createdAt);
CREATE INDEX idx_users_updated ON users(updatedAt);

-- Sessions table indexes
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_user ON sessions(userId);
CREATE INDEX idx_sessions_expires ON sessions(expiresAt);
CREATE INDEX idx_sessions_created ON sessions(createdAt);

-- Accounts table indexes  
CREATE INDEX idx_accounts_user ON accounts(userId);
CREATE INDEX idx_accounts_provider ON accounts(providerId);
CREATE INDEX idx_accounts_provider_account ON accounts(providerId, accountId);
CREATE INDEX idx_accounts_expires ON accounts(expiresAt);
```

### Cleanup Procedures

```sql
-- Clean up expired sessions (run periodically)
DELETE FROM sessions 
WHERE expiresAt < CURRENT_TIMESTAMP;

-- Clean up expired OAuth tokens (run periodically)
UPDATE accounts 
SET accessToken = NULL, refreshToken = NULL 
WHERE expiresAt < CURRENT_TIMESTAMP;
```

---

## 🔐 Security Considerations

### Field Constraints and Validation

```sql
-- Add additional constraints for security
ALTER TABLE users 
ADD CONSTRAINT chk_email_format 
CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE users
ADD CONSTRAINT chk_role_values
CHECK (role IN ('admin', 'super_admin', 'user'));

ALTER TABLE sessions
ADD CONSTRAINT chk_token_length
CHECK (LENGTH(token) >= 32);

ALTER TABLE accounts
ADD CONSTRAINT chk_provider_values
CHECK (providerId IN ('google', 'github', 'microsoft', 'apple'));
```

### Data Encryption (Application Level)

```typescript
// Note: These should be implemented in your external API backend
interface SecurityMeasures {
  // Hash passwords using bcrypt (min 12 rounds)
  passwordHashing: 'bcrypt',
  
  // Encrypt sensitive tokens
  tokenEncryption: 'AES-256-GCM',
  
  // Session token security
  tokenGeneration: 'cryptographically-secure-random',
  
  // Database connections
  connectionSecurity: 'TLS/SSL-required'
}
```

---

## 🌐 Database Environment Configuration

### Development Environment

```sql
-- Development database setup
CREATE DATABASE lunaxcode_dev_auth;
USE lunaxcode_dev_auth;

-- Create tables (run all CREATE TABLE statements above)
-- Insert sample data for testing
```

### Production Environment

```sql
-- Production database setup
CREATE DATABASE lunaxcode_prod_auth;
USE lunaxcode_prod_auth;

-- Create tables with production-ready settings
-- Set appropriate timezone
SET time_zone = '+08:00'; -- Philippines timezone

-- Enable performance optimizations
SET innodb_buffer_pool_size = 1GB; -- Adjust based on server capacity
```

### Environment Variables

```env
# Database Configuration for External API
DB_HOST=your-database-host
DB_PORT=3306
DB_NAME=lunaxcode_auth
DB_USER=lunaxcode_user
DB_PASSWORD=secure-password-here
DB_SSL=true

# Better Auth Configuration
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars
BETTER_AUTH_URL=https://lunaxcode.com
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
```

---

## 📋 Implementation Checklist

### Database Setup
- [ ] Create `users` table with proper constraints
- [ ] Create `sessions` table with foreign keys
- [ ] Create `accounts` table for OAuth
- [ ] Add all recommended indexes
- [ ] Set up cleanup procedures

### Data Migration
- [ ] Backup existing `cms_users` table
- [ ] Run migration script to populate `users` table
- [ ] Verify data integrity after migration
- [ ] Test authentication with migrated users

### Security Implementation
- [ ] Add field validation constraints
- [ ] Implement password hashing (bcrypt)
- [ ] Set up token encryption
- [ ] Configure database SSL/TLS
- [ ] Set up automated cleanup jobs

### Testing
- [ ] Test user registration flow
- [ ] Test email/password authentication
- [ ] Test Google OAuth flow
- [ ] Test session management
- [ ] Test user role verification
- [ ] Verify all indexes are working

### Monitoring
- [ ] Set up database performance monitoring
- [ ] Monitor session cleanup effectiveness
- [ ] Track authentication success/failure rates
- [ ] Monitor for security anomalies

---

## 🔧 Maintenance Tasks

### Daily Tasks
- Monitor authentication logs for anomalies
- Check database performance metrics

### Weekly Tasks
- Clean up expired sessions
- Review user access patterns
- Update OAuth tokens if needed

### Monthly Tasks
- Review and rotate secrets
- Analyze authentication metrics
- Update security patches
- Backup authentication database

---

## 📚 Additional Resources

### Better Auth Documentation
- [Better Auth Database Schema](https://better-auth.com/docs/database)
- [OAuth Provider Setup](https://better-auth.com/docs/social-auth)
- [Session Management](https://better-auth.com/docs/sessions)

### Database Best Practices
- [MySQL Performance Tuning](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [Database Index Optimization](https://use-the-index-luke.com/)

---

**Last Updated:** January 2025  
**Version:** 1.0  
**Maintained by:** Lunaxcode Development Team
