# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Development Commands

### Starting the Application
```bash
# Start development server
python start_dev.py

# Manual start with uvicorn (if needed)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Database Operations
```bash
# Seed database with sample data
python seed.py

# Alternative comprehensive seeding
python scripts/comprehensive_seed.py
```

### Dependencies
```bash
# Install dependencies
pip install -r docs/requirements.txt

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## 🏗️ Architecture Overview

This is a **FastAPI-based CMS Admin API** for Lunaxcode.com with the following architecture:

### Core Structure
```
app/
├── api/v1/          # API endpoints (auth, content management)
├── core/            # Configuration, exceptions, logging, middleware
├── database/        # PostgreSQL/Xata connection, migrations
├── models/          # Pydantic schemas (database.py, schemas.py)
└── services/        # Business logic layer
```

### Technology Stack
- **FastAPI** with Pydantic v2 for data validation
- **PostgreSQL** via Xata serverless database
- **Redis** for caching (optional, falls back gracefully)
- **JWT Authentication** with role-based access
- **SQLAlchemy** for database operations

### Database Design
- **Multi-tenant ready**: All tables include Xata standard fields (`xata_id`, `xata_version`, etc.)
- **Content Management**: pricing_plans, features, process_steps, hero_section, testimonials, faqs, site_settings, addon_services
- **New Onboarding System**: Complex multi-step onboarding flow with progress tracking and analytics

## 🔐 Authentication System

### Demo Credentials
- **Admin**: `admin@lunaxcode.com` / `admin123`
- **Editor**: `editor@lunaxcode.com` / `editor123`

### JWT Configuration
- **Expiration**: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Algorithm**: HS256
- **Headers**: `Authorization: Bearer <token>`

## 📊 API Endpoints

### Base URLs
- **Development**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health

### Standard CRUD Pattern
All content endpoints follow this pattern:
- `POST /api/v1/{endpoint}/` - Create
- `GET /api/v1/{endpoint}/` - List all (with pagination)
- `GET /api/v1/{endpoint}/{id}` - Get by ID
- `PATCH /api/v1/{endpoint}/{id}` - Update
- `DELETE /api/v1/{endpoint}/{id}` - Delete
- `GET /api/v1/{endpoint}/search/{query}` - Search

### Core Endpoints
- `/api/v1/auth/*` - Authentication
- `/api/v1/pricing-plans` - Service packages
- `/api/v1/features` - Product features
- `/api/v1/onboarding/*` - Multi-step onboarding system
- `/api/v1/testimonials`, `/api/v1/faqs`, etc.

## ⚠️ Important Development Guidelines

### Pydantic v2 Usage
- Follow **type-first approach** with extensive type hints
- Use `BaseModel` for all data structures
- Leverage built-in validators (`EmailStr`, `conint`, etc.)
- Prefer `model_validate_json()` over `model_validate(json.loads())`
- Handle `ValidationError` exceptions properly

### Database Operations
- **Database connection**: Uses `app.database.postgres.db_manager`
- **Connection testing**: Built-in health checks via `/health`
- **Xata Integration**: All tables use Xata standard fields
- **Migration system**: Available in `app.database.migrations.py`

### Environment Configuration
- **Required**: `DATABASE_URL` (Xata PostgreSQL connection)
- **Optional**: `REDIS_URL` (caching layer)
- **Security**: `SECRET_KEY`, `XATA_API_KEY`
- **Development**: Copy `.env.example` to `.env`

### Code Organization Patterns
- **Services Layer**: Business logic separated from API endpoints
- **Pydantic Models**: Database schemas in `models/database.py`, API schemas in `models/schemas.py`
- **Exception Handling**: Centralized in `core/exceptions.py`
- **Logging**: Structured logging via `core/logging.py`

### Testing Notes
- **No existing test suite** - create tests using `pytest` and `httpx`
- **Test data**: Use seeding scripts in `scripts/` directory
- **API Testing**: Use interactive docs at `/api/v1/docs` for manual testing

## 🚨 Critical Considerations

### Onboarding System Complexity
- **Multi-step flow** with progress tracking and conditional logic
- **Service-specific customization** and validation schemas
- **Analytics integration** for step completion tracking
- See `docs/onboarding-schema-documentation.md` for detailed schema

### Database Migration
- **Recent migration** from Xata to PostgreSQL (some references may remain)
- **Connection testing** implemented for reliability
- **Graceful fallbacks** for Redis cache failures

### Development Workflow
1. Ensure `.env` is configured with database credentials
2. Start with `python start_dev.py` (includes startup checks)
3. Use database seeding scripts for test data
4. API documentation available at `/api/v1/docs` for endpoint testing