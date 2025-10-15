# Development Guide

## API Documentation
Access API documentation at http://localhost:8000/docs

## uv Package Manager Setup
Install uv on Windows:
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Project Initialization
Create new project:
```bash
uv init social-network
```

Add FastAPI dependencies:
```bash
uv add fastapi uvicorn
```

Select Python interpreter in VS Code:
```
ctrl+shift+p
```

## Running the Application
Start development server:
```bash
uv run uvicorn main:app --reload
```

## Database Setup
Connect to PostgreSQL:
```bash
psql -h localhost -p 5432 -U postgres -d social_network
```

Clean existing database types:
```sql
DROP TYPE IF EXISTS gender CASCADE;
```

## Dependencies Installation
Install all required packages:
```bash
uv add sqlalchemy psycopg2-binary passlib[bcrypt] email-validator alembic python-dotenv pydantic-settings asyncpg loguru pyjwt faker
```

## Database Migrations
Initialize Alembic:
```bash
uv run alembic init alembic
```

Create migration (default environment):
```bash
uv run alembic revision --autogenerate -m "Create users table"
```

Create migration (production environment):
```bash
ENV_FILE=.env.prod uv run alembic revision --autogenerate -m "Create users table"
```

Apply migrations:
```bash
uv run alembic upgrade head
```

Apply migrations with verbose output:
```bash
uv run alembic -x verbose=true revision --autogenerate -m "Create users table"
```

Connect to database:
```bash
psql -h localhost -p 5432 -U postgres -d social_network
```

Verify migration status:
```bash
uv run alembic current
```

Downgrade to previous version:
```bash
uv run alembic downgrade -1
```

Downgrade to base (empty database):
```bash
uv run alembic downgrade base
```

## Docker Operations
Execute database commands in Docker:
```bash
docker-compose exec -T db psql -U postgres -d social_network -c "\dt"
```

Navigate to project directory:
```bash
cd social-network
```

Start development environment:
```bash
docker-compose up -d
```

Start production environment:
```bash
docker-compose --env-file .env.prod up
```

Start database only:
```bash
docker-compose up -d db
```

## Environment Variables
Load environment variables in PowerShell:
```powershell
Get-Content .env | Where-Object {$_ -and !$_.StartsWith("#")} | ForEach-Object {$parts = $_ -split "=",2; [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")}
```

Check specific environment variable:
```powershell
$env:POSTGRES_HOST
```

uv run uvicorn main:app --reload

cmd /c setup-replication.bat

uv run pytest tests/test_bulk_insert.py -v