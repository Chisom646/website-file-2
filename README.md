# People Help The People

A mental health and abuse survivor support community platform built with FastAPI, SQLModel, and PostgreSQL.

## Features

- 🔐 User registration and JWT-based authentication
- 👤 User profiles with personal information
- 🏥 Support group features (coming soon)
- 💬 Community posts and discussions (coming soon)
- 📱 Responsive web interface

## Tech Stack

- **Backend**: FastAPI 0.104+, Python 3.11+
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Frontend**: Vanilla HTML/CSS/JavaScript

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Local Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd website-file-2
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install the Package

```bash
pip install -e .
```

This will install the `people-help` command and all dependencies.

**Note**: If you see a warning about the script not being on PATH:
```
WARNING: The script people-help is installed in '...' which is not on PATH.
```

You can either:
- Add the directory to your PATH, OR
- Use `python3 -m people_help` instead (works without PATH changes)

### 4. Set Up PostgreSQL Database

Create a PostgreSQL database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE people_help_db;

# Create user (optional, if not using postgres user)
CREATE USER people_help_app WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE people_help_db TO people_help_app;
\q
```

### 5. Configure Environment Variables

Create a `.env` file in the `people_help/` directory:

```bash
# people_help/.env

# Database Configuration
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=people_help_db

# JWT Configuration
SECRET_KEY=your_secret_key_here_at_least_32_characters_long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=true
ENVIRONMENT=development
```

**⚠️ Important**: Generate a strong secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Initialize the Database

Run the setup script to create tables and default roles:

```bash
python3 people_help/setup.py
```

Expected output:
```
🔄 Setting up database...
✅ Tables created successfully
✅ Default roles initialized

🎉 Setup completed successfully!
```

### 7. Start the Server

You can start the server in multiple ways:

**Option A: Using the CLI command (recommended)**
```bash
people-help --reload
```

**Option B: Using Python module**
```bash
python3 -m people_help --reload
```

**Option C: Direct uvicorn (if needed)**
```bash
uvicorn people_help.main:app --reload --port 8888
```

The API will be available at:
- **API**: http://localhost:8888
- **API Docs**: http://localhost:8888/docs
- **ReDoc**: http://localhost:8888/redoc

### 8. Serve the Frontend

In a separate terminal, serve the HTML files:

```bash
# Using Python's built-in HTTP server
python3 -m http.server 5500

# Or use any other static file server
# npm install -g http-server
# http-server -p 5500
```

Access the application at:
- **Landing Page**: http://localhost:5500/landing.html
- **Sign Up**: http://localhost:5500/signup.html
- **Login**: http://localhost:5500/login.html

## CLI Usage

The `people-help` command supports several options:

```bash
# Start with auto-reload (development)
people-help --reload

# Specify custom port
people-help --port 9000

# Change host binding
people-help --host 127.0.0.1 --port 8080

# Adjust log level
people-help --log-level debug

# Production mode with multiple workers
people-help --workers 4 --log-level info

# Skip environment validation (not recommended)
people-help --no-env-check
```

View all options:
```bash
people-help --help
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_NAME` | Database name | `people_help_db` |
| `SECRET_KEY` | JWT signing key (min 32 chars) | `<generated-secret>` |

### Optional Variables with Defaults

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DB_PORT` | Database port | `5432` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | `30` |
| `DEBUG` | Debug mode | `false` |
| `ENVIRONMENT` | Environment name | `production` |
| `PORT` | Server port (CLI default) | `8888` |

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/profile` - Get current user profile (requires auth)
- `GET /api/auth/check-username/{username}` - Check username availability
- `GET /api/auth/check-email/{email}` - Check email availability

### Health Check

- `GET /` - API root message
- `GET /health` - Health check endpoint

Full interactive API documentation available at http://localhost:8888/docs

## Project Structure

```
.
├── people_help/              # Main package (formerly 'app/')
│   ├── __init__.py
│   ├── __main__.py          # Enables 'python -m people_help'
│   ├── cli.py               # CLI entry point
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration and database
│   ├── setup.py             # Database initialization script
│   ├── .env                 # Environment variables (not in git)
│   │
│   ├── models/              # SQLModel database models
│   │   ├── user.py
│   │   ├── person.py
│   │   ├── role.py
│   │   └── user_role.py
│   │
│   ├── repositories/        # Data access layer
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   └── person_repository.py
│   │
│   ├── routes/              # API endpoints
│   │   └── auth_routes.py
│   │
│   ├── services/            # Business logic
│   │   └── auth_service.py
│   │
│   ├── schemas/             # Pydantic request/response schemas
│   │   └── auth.py
│   │
│   ├── dependencies/        # FastAPI dependencies
│   │   └── auth.py
│   │
│   └── utils/               # Utility modules
│       ├── security.py      # Password hashing, JWT
│       └── exceptions.py    # Custom exceptions
│
├── *.html                   # Frontend pages
├── auth.js                  # Frontend API client
├── style.css                # Global styles
├── images/                  # Static assets
│
├── pyproject.toml           # Package metadata and dependencies
├── README.md                # This file
└── .gitignore              # Git ignore rules

```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (when implemented)
pytest
```

### Database Migrations

The project currently uses `SQLModel.metadata.create_all()` for schema management. For production, consider implementing Alembic migrations.

### Code Style

This project follows standard Python conventions:
- PEP 8 for code style
- Type hints where appropriate
- Async/await for all I/O operations

## Troubleshooting

### "Module 'people_help' has no attribute 'cli'"

Make sure you've installed the package with `pip install -e .`

### "Failed to connect to database"

1. Verify PostgreSQL is running: `pg_isready`
2. Check `.env` file has correct credentials
3. Ensure database exists: `psql -U postgres -l`

### "Missing required environment variables"

The CLI validates required env vars by default. Either:
1. Create a proper `.env` file in `people_help/` directory
2. Export variables in your shell
3. Use `--no-env-check` flag (not recommended)

### Port already in use

Change the port with:
```bash
people-help --port 9000
```

Or set the `PORT` environment variable.

### CORS errors in frontend

Ensure backend is running on port 8888 and frontend is on port 5500. The CORS configuration allows:
- Backend: 8000, 8888
- Frontend: 3000, 5500

## Security Notes

- **Never commit `.env` files** to version control
- Generate strong random secret keys using `secrets.token_urlsafe(32)`
- Use HTTPS in production
- Enable rate limiting in production
- Review CORS origins for production deployment

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check the API docs at `/docs`

---

**Built with ❤️ for mental health support communities**
