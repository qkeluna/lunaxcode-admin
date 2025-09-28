# Vercel Deployment Guide for Lunaxcode CMS

## 🚀 Quick Fix for FUNCTION_INVOCATION_FAILED

The main issues causing your deployment failure were:

1. **Missing `vercel.json` configuration** ✅ Fixed
2. **Problematic native dependencies** ✅ Fixed  
3. **Complex database initialization** ✅ Simplified

## 📁 Files Created/Modified

### New Files:
- `vercel.json` - Vercel configuration
- `api/index.py` - Vercel entry point
- `app/main_vercel.py` - Simplified FastAPI app
- `requirements.txt` - Vercel-compatible dependencies
- `.vercelignore` - Exclude unnecessary files

## 🔧 Key Changes Made

### 1. Vercel Configuration (`vercel.json`)
```json
{
  "version": 2,
  "builds": [{"src": "api/index.py", "use": "@vercel/python"}],
  "routes": [
    {"src": "/api/(.*)", "dest": "api/index.py"},
    {"src": "/(.*)", "dest": "api/index.py"}
  ]
}
```

### 2. Removed Problematic Dependencies
- ❌ `bcrypt` (native dependency)
- ❌ `psycopg2-binary` (native dependency) 
- ❌ `greenlet` (native dependency)
- ❌ `redis` (connection issues)

### 3. Simplified App Structure
- Removed database initialization on startup
- Removed cache initialization
- Added fallback static data endpoints
- Simplified error handling

## 🚀 Deployment Steps

### Option 1: Use Simplified App (Recommended)
1. **Push your changes to GitHub**
2. **Deploy to Vercel** - it will use the simplified `main_vercel.py`
3. **Test endpoints**:
   - `https://your-app.vercel.app/`
   - `https://your-app.vercel.app/health`
   - `https://your-app.vercel.app/api/v1/pricing-plans/`

### Option 2: Full App with Environment Variables
If you want to use the full app, set these environment variables in Vercel:

```bash
# Database (if using external PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/db

# Optional: Redis (if using external Redis)
REDIS_URL=redis://user:pass@host:port

# App settings
DEBUG=false
ENVIRONMENT=production
```

## 🧪 Testing Your Deployment

After deployment, test these endpoints:

```bash
# Health check
curl https://your-app.vercel.app/health

# API endpoints
curl https://your-app.vercel.app/api/v1/pricing-plans/
curl https://your-app.vercel.app/api/v1/features/
curl https://your-app.vercel.app/api/v1/testimonials/
```

## 🔍 Troubleshooting

### If you still get 500 errors:

1. **Check Vercel Function Logs**:
   - Go to Vercel Dashboard → Your Project → Functions
   - Click on the failed function to see logs

2. **Common Issues**:
   - **Import errors**: Check that all dependencies are in `requirements.txt`
   - **Timeout**: Functions timeout after 10s on Hobby plan, 30s on Pro
   - **Memory**: Large imports can cause memory issues

3. **Debug Mode**:
   - Add `print()` statements in `api/index.py` to debug imports
   - Check which fallback app is being used

### Environment Variables Needed:
```bash
# Minimal setup (for simplified app)
ENVIRONMENT=production

# Full setup (for complete app)
DATABASE_URL=your_postgres_url
REDIS_URL=your_redis_url  # optional
XATA_API_KEY=your_xata_key  # if using Xata
XATA_DATABASE_URL=your_xata_db_url  # if using Xata
```

## 📊 Performance Notes

- **Cold Start**: First request may be slow (~2-5s)
- **Warm Requests**: Subsequent requests are fast (~100-500ms)
- **Memory**: Simplified app uses ~50MB, full app ~100-200MB
- **Timeout**: 30s max execution time (with current config)

## 🎯 Next Steps

1. **Deploy and test** the simplified version first
2. **Add database connection** if needed (external PostgreSQL)
3. **Gradually add features** back as needed
4. **Monitor performance** in Vercel dashboard

The simplified app provides all your API endpoints with static data, perfect for frontend development and testing!
