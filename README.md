# People Help The People

A mental health and abuse survivor support community platform built with FastAPI, SQLModel, and PostgreSQL.

## Features

- 🔐 User registration and JWT-based authentication with rate limiting
- 👤 User profiles with personal information
- 🌍 Multi-language support (English, Yoruba, Hausa, Igbo)
- 🏥 Support communities with membership management
- 💬 Real-time WebSocket chat for communities
- 📝 User feed with posts (general and community-specific)
- 🛡️ Permission-based content management
- 📱 Responsive web interface
- 📊 Structured logging and security best practices

## Tech Stack

- **Backend**: FastAPI 0.104+, Python 3.11+
- **Database**: PostgreSQL 14+ with SQLModel ORM and AsyncPG
- **Authentication**: JWT tokens with bcrypt password hashing
- **Real-time**: WebSocket support for chat
- **Security**: slowapi rate limiting, structured logging
- **i18n**: Multi-language support (translation-ready infrastructure)
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

Create a `.env` file in the `people_help/` directory (use `.env.example` as template):

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

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Translation (i18n)
# IMPORTANT: Translation is currently DISABLED
# Set to true only when translation files are ready
TRANSLATION_ENABLED=false
```

**⚠️ Important**: Generate a strong secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Initialize the Database

**Option A: Automatic setup (Recommended)**

The database tables will be created automatically when you first start the server. The application uses SQLModel's `create_all()` during startup.

**Option B: Manual setup with migrations**

Apply database migrations manually for additional schema changes:

```bash
# Apply all migrations in order
psql -U your_db_user -d people_help_db -f people_help/migrations/001_add_language_to_users.sql
psql -U your_db_user -d people_help_db -f people_help/migrations/002_create_communities_tables.sql
psql -U your_db_user -d people_help_db -f people_help/migrations/003_create_posts_table.sql
```

See [people_help/migrations/README.md](people_help/migrations/README.md) for detailed migration documentation.

**Option C: Legacy setup script**

If available, run the setup script to create tables and default roles:

```bash
python3 people_help/setup.py
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
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `true` |
| `RATE_LIMIT_PER_MINUTE` | General rate limit | `60` |
| `TRANSLATION_ENABLED` | Enable i18n translation | `false` |

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user (rate limited: 5/min)
- `POST /api/auth/login` - Login and get JWT token (rate limited: 10/min)
- `GET /api/auth/profile` - Get current user profile (requires auth)
- `GET /api/auth/check-username/{username}` - Check username availability
- `GET /api/auth/check-email/{email}` - Check email availability
- `GET /api/auth/languages` - Get supported languages
- `PUT /api/auth/language` - Update user language preference (requires auth)

### Communities
- `GET /api/communities` - List all communities with membership status (requires auth)
- `POST /api/communities/{community_id}/join` - Join a community (requires auth)
- `POST /api/communities/{community_id}/leave` - Leave a community (requires auth)
- `GET /api/communities/{community_id}/messages` - Get chat messages (requires auth, members only)
- `WS /api/communities/{community_id}/ws` - WebSocket for real-time chat (requires auth)

### Feed
- `POST /api/posts` - Create a new post (requires auth)
- `GET /api/posts` - Get feed posts, optionally filtered by community (requires auth)
- `DELETE /api/posts/{post_id}` - Delete a post (requires auth, author or admin only)

### Health Check
- `GET /` - API root message
- `GET /health` - Health check endpoint with rate limiting status

Full interactive API documentation available at http://localhost:8888/docs

## Project Structure

```
.
├── people_help/              # Main package
│   ├── __init__.py
│   ├── __main__.py          # Enables 'python -m people_help'
│   ├── cli.py               # CLI entry point
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration and database
│   ├── setup.py             # Database initialization script
│   ├── .env                 # Environment variables (not in git)
│   ├── .env.example         # Environment variables template
│   │
│   ├── models/              # SQLModel database models
│   │   ├── user.py          # User authentication model
│   │   ├── person.py        # Person profile model
│   │   ├── role.py          # Role model
│   │   ├── user_role.py     # User-role association
│   │   ├── community.py     # Community models
│   │   └── post.py          # Feed post model
│   │
│   ├── routes/              # API endpoints
│   │   ├── auth_routes.py   # Authentication endpoints
│   │   ├── community_routes.py  # Community and chat endpoints
│   │   └── feed_routes.py   # Feed/posts endpoints
│   │
│   ├── i18n/                # Internationalization
│   │   ├── __init__.py      # Language configuration
│   │   └── translator.py    # Translation service (stubbed)
│   │
│   ├── migrations/          # Database migrations
│   │   ├── README.md        # Migration documentation
│   │   ├── 001_add_language_to_users.sql
│   │   ├── 002_create_communities_tables.sql
│   │   └── 003_create_posts_table.sql
│   │
│   ├── utils/               # Utility modules
│   │   ├── security.py      # Password hashing, JWT
│   │   └── exceptions.py    # Custom exceptions
│   │
│   └── [legacy directories]  # repositories/, services/, schemas/, dependencies/
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

The project uses SQL migration files in `people_help/migrations/` for schema changes:
- Migrations are idempotent (use `IF NOT EXISTS` clauses)
- Apply manually using `psql` (see [migrations/README.md](people_help/migrations/README.md))
- Base tables are created automatically via `SQLModel.metadata.create_all()` on startup
- For production, consider implementing Alembic for automated migration tracking

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
- Rate limiting is enabled by default (5/min registration, 10/min login, 60/min general)
- Review CORS origins for production deployment
- Password minimum length: 6 characters
- JWT tokens expire after 30 minutes (configurable)
- Passwords are hashed with bcrypt before storage
- Permission checks enforce content ownership (posts, communities)

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
