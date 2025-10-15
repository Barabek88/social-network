# Social Network API

FastAPI-based social network application with JWT authentication and PostgreSQL database.

## Features
- User registration and authentication
- JWT token-based security
- PostgreSQL database with async SQLAlchemy
- Docker containerization
- Database migrations with Alembic

## Quick Start

### Using Docker (Recommended)
```bash
# Clone repository
git clone <repo-url>
cd social-network

# Start services
docker-compose up -d

# Access API documentation
# http://localhost:8000/docs
```

## API Endpoints
- `POST /api/v1/user/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/user/get/{user_id}` - Get user by ID (requires authentication)
- `Get /api/v1/user/search` - Search user by first_name and second_name

## Environment Variables
Required environment variables (see `.env.example`):
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=social_network
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_TIME=3600
```

## Development
For detailed development instructions, database operations, and advanced configuration, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Docker Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Testing
Use the interactive API documentation at http://localhost:8000/docs to test endpoints.

Postman collection available in `postman/` folder..

Fill db with test data
uv run python scripts\fill_test_data.py

## Architecture
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM with async support
- **Alembic** - Database migrations
- **JWT** - Authentication tokens
- **Docker** - Containerization
- **Loguru** - Structured logging

docker-compose up -d db db-slave1 db-slave2



