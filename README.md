# Lunaxcode CMS Admin API

A comprehensive FastAPI backend for managing Lunaxcode.com content, built with modern Python technologies and integrated with Xata PostgreSQL database.

## 🚀 Features

- **FastAPI Framework**: High-performance, modern Python web framework
- **Xata Integration**: Serverless PostgreSQL database with automatic scaling
- **Redis Caching**: High-performance caching layer for improved response times
- **Authentication & Authorization**: JWT-based auth with role-based permissions
- **Comprehensive CRUD APIs**: Full content management for all site sections
- **Input Validation**: Pydantic models with automatic validation
- **API Documentation**: Interactive OpenAPI/Swagger documentation
- **Error Handling**: Comprehensive error handling with detailed logging
- **Testing Ready**: Structured for easy unit and integration testing

## 📊 Content Management

The API manages all content for Lunaxcode.com including:

- **Pricing Plans**: Service packages and pricing tiers
- **Features**: Key product/service highlights
- **Process Steps**: Service workflow documentation
- **Hero Section**: Landing page main content
- **Testimonials**: Client reviews and feedback
- **Contact Info**: Contact details and social links
- **FAQs**: Frequently asked questions
- **Site Settings**: Global configuration
- **Addon Services**: Additional service offerings

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **Xata**: Serverless PostgreSQL database
- **Redis**: In-memory data structure store for caching
- **JWT**: JSON Web Tokens for authentication
- **Uvicorn**: ASGI server for running the application
- **Python 3.9+**: Modern Python with async/await support

## 🔐 Better Auth Migration

This project now supports Better Auth for authentication. To migrate your database:

```bash
# Run the Better Auth migration
python scripts/migrate_better_auth.py
```

For detailed migration instructions, see: [Better Auth Migration Guide](docs/better-auth-migration-guide.md)

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd lunaxcode-admin
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r docs/requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Configure your .env file**:
   ```env
   ENVIRONMENT=development
   DEBUG=true
   SECRET_KEY=your-super-secret-key
   XATA_API_KEY=your_xata_api_key
   XATA_DATABASE_URL=your_xata_database_url
   REDIS_URL=redis://localhost:6379
   ```

## 🚀 Running the Application

### Development Server

```bash
python start_dev.py
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### Production Server

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. There are demo credentials available:

### Demo Users
- **Admin**: `admin@lunaxcode.com` / `admin123`
- **Editor**: `editor@lunaxcode.com` / `editor123`

### Authentication Flow

1. **Login**: POST `/api/v1/auth/login` with email/password
2. **Get Token**: Receive JWT access token
3. **Use Token**: Include in Authorization header: `Bearer <token>`
4. **Refresh**: Tokens expire after 30 minutes (configurable)

### API Endpoints

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@lunaxcode.com", "password": "admin123"}'

# Use authenticated endpoint
curl -X GET "http://localhost:8000/api/v1/pricing-plans" \
  -H "Authorization: Bearer <your-token>"
```

## 📖 API Documentation

### Core Endpoints

#### Content Management
- **Pricing Plans**: `/api/v1/pricing-plans`
- **Features**: `/api/v1/features`
- **Process Steps**: `/api/v1/process-steps`
- **Hero Section**: `/api/v1/hero-section`
- **Testimonials**: `/api/v1/testimonials`
- **Contact Info**: `/api/v1/contact-info`
- **FAQs**: `/api/v1/faqs`
- **Site Settings**: `/api/v1/site-settings`
- **Addon Services**: `/api/v1/addon-services`

#### Authentication
- **Login**: `POST /api/v1/auth/login`
- **Logout**: `POST /api/v1/auth/logout`
- **Current User**: `GET /api/v1/auth/me`
- **Verify Token**: `POST /api/v1/auth/verify-token`

#### System
- **Health Check**: `GET /health`
- **API Root**: `GET /`

### Standard CRUD Operations

Each content endpoint supports:

- **CREATE**: `POST /api/v1/{endpoint}/`
- **READ ALL**: `GET /api/v1/{endpoint}/`
- **READ ONE**: `GET /api/v1/{endpoint}/{id}`
- **UPDATE**: `PATCH /api/v1/{endpoint}/{id}`
- **DELETE**: `DELETE /api/v1/{endpoint}/{id}`
- **SEARCH**: `GET /api/v1/{endpoint}/search/{query}`

### Query Parameters

- **Pagination**: `?page=1&size=20`
- **Filtering**: `?category=web&active_only=true`
- **Sorting**: Automatic by `displayOrder` field

## 🗄️ Database Schema

The application uses Xata PostgreSQL with the following tables:

- `pricing_plans` - Service pricing and packages
- `features` - Product/service features
- `process_steps` - Workflow steps
- `hero_section` - Landing page hero content
- `testimonials` - Client testimonials
- `contact_info` - Contact information
- `faqs` - Frequently asked questions
- `site_settings` - Global settings
- `addon_services` - Additional services

Each table includes automatic Xata fields:
- `xata_id` - Unique identifier
- `xata_version` - Version control
- `xata_createdat` - Creation timestamp
- `xata_updatedat` - Update timestamp

## 🚦 Testing

### Manual Testing

Use the interactive API documentation at `/api/v1/docs` to test endpoints.

### Automated Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## 📝 Development

### Project Structure

```
lunaxcode-admin/
├── app/
│   ├── api/
│   │   └── v1/          # API version 1 endpoints
│   ├── core/            # Core functionality
│   ├── database/        # Database configuration
│   ├── models/          # Pydantic models
│   ├── services/        # Business logic
│   └── main.py          # FastAPI application
├── docs/                # Documentation
├── logs/                # Application logs
├── tests/               # Test files
├── .env.example         # Environment template
├── start_dev.py         # Development server
└── requirements.txt     # Dependencies
```

### Adding New Endpoints

1. Create Pydantic models in `app/models/`
2. Add service layer in `app/services/`
3. Create API endpoints in `app/api/v1/`
4. Register router in `app/api/__init__.py`

### Environment Variables

See `.env.example` for all available configuration options.

## 🛡️ Security

- JWT authentication with configurable expiration
- Rate limiting on authentication endpoints
- Input validation with Pydantic
- CORS configuration
- Environment-based configuration
- Comprehensive logging

## 📊 Monitoring

- Health check endpoint: `/health`
- Structured logging with different levels
- Performance timing headers
- Redis connection monitoring

## 🚀 Deployment

### Docker (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### Environment Setup

For production deployment:

1. Set `ENVIRONMENT=production`
2. Set `DEBUG=false`
3. Use strong `SECRET_KEY`
4. Configure proper `ALLOWED_HOSTS`
5. Set up Redis instance
6. Configure logging

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support and questions:
- Email: hello@lunaxcode.com
- GitHub Issues: Create an issue in this repository

---

Built with ❤️ by the Lunaxcode team