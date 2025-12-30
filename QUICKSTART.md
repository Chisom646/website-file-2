# Quick Start Guide

## 🚀 Get Running in 5 Minutes

This guide will get you from fresh clone to running application.

## Prerequisites

- **Python 3.11+** (`python3 --version`)
- **PostgreSQL 12+** (with `psql` and `createdb` commands)
- **Git** (already installed if you cloned the repo)

## Setup Steps

### Step 1: Clone & Navigate

```bash
git clone <repository-url>
cd website-file-2
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Important**: You'll see `(venv)` in your prompt when activated. Always activate before working!

### Step 3: Install Dependencies

```bash
pip install -e .
```

✅ This installs all dependencies including:
- FastAPI, SQLModel, AsyncPG
- bcrypt, python-jose (auth)
- slowapi (rate limiting)
- uvicorn (server)

### Step 4: Set Up Environment Variables

```bash
# Copy the example env file
cp people_help/.env.example people_help/.env
```

**Edit `people_help/.env`** with these required settings:

```env
# Database Configuration
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=people_help_db

# JWT Configuration - REQUIRED!
# Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your_generated_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=true
ENVIRONMENT=development

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Translation (keep disabled)
TRANSLATION_ENABLED=false
```

**Generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output and paste it as your `SECRET_KEY` value.

### Step 5: Create PostgreSQL Database

**Option A - Using createdb:**
```bash
createdb people_help_db
```

**Option B - Using psql:**
```bash
psql -U postgres
CREATE DATABASE people_help_db;
\q
```

**Option C - Using Homebrew PostgreSQL (macOS):**
```bash
/usr/local/opt/postgresql@14/bin/createdb people_help_db
```

### Step 6: Apply Database Migrations

The database tables will be created automatically on first start, but you can manually apply migrations:

```bash
# Apply all migrations in order
psql -U postgres -d people_help_db -f people_help/migrations/001_add_language_to_users.sql
psql -U postgres -d people_help_db -f people_help/migrations/002_create_communities_tables.sql
psql -U postgres -d people_help_db -f people_help/migrations/003_create_posts_table.sql
```

**Seed default communities:**
The backend will automatically create 3 default communities on first run:
- Mindful Moments
- Healing Together
- Calm Circle

### Step 7: Start Backend Server

```bash
# Make sure venv is activated
python3 -m people_help --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8888
INFO:     🚀 Starting server...
INFO:     Rate limiting: enabled
INFO:     Rate limit: 60 requests/minute per IP
INFO:     ✅ Database initialized successfully
```

Server is now running at: **http://localhost:8888**

### Step 8: Serve Frontend (New Terminal)

Open a **new terminal** (keep the backend running), then:

```bash
cd /path/to/website-file-2
python3 -m http.server 5500
```

Expected output:
```
Serving HTTP on 0.0.0.0 port 5500 (http://0.0.0.0:5500/) ...
```

Frontend is now available at: **http://localhost:5500**

### Step 9: Access the Application

Open your browser and navigate to:

1. **Landing Page**: http://localhost:5500/landing.html
2. **Sign Up**: http://localhost:5500/signup.html
3. **Login**: http://localhost:5500/login.html
4. **Dashboard**: http://localhost:5500/dashboard.html (after login)
5. **Communities**: http://localhost:5500/communities.html (after login)
6. **Profile**: http://localhost:5500/profile.html (after login)

**API Documentation**: http://localhost:8888/docs

---

## 🎯 Quick Test (2 Minutes)

After setup, verify everything works:

### Test 1: Register & Login
1. Go to http://localhost:5500/signup.html
2. Register with: username=`testuser`, email=`test@example.com`, password=`test123456`
3. Login with same credentials
4. Should redirect to Dashboard

### Test 2: Create Post
1. On Dashboard, type a message in "Share Your Thoughts"
2. Click "Post"
3. Post should appear in feed below
4. Click "Delete" to remove it

### Test 3: Join Community & Chat
1. Click "Communities" in navigation
2. Click "Join" on "Mindful Moments"
3. Click "Chat" button
4. Type a message and press Enter
5. Message should appear instantly

### Test 4: Real-Time Chat (Two Browsers)
1. Open second browser/incognito window
2. Register another user (e.g., `testuser2`)
3. Join same community and open chat
4. Send messages from both browsers
5. **Verify**: Messages appear in real-time in both windows

✅ **If all 4 tests pass, setup is complete!**

---

## 📂 Project Structure

```
website-file-2/
├── people_help/              # Backend (Python/FastAPI)
│   ├── models/               # Database models
│   ├── routes/               # API endpoints
│   ├── migrations/           # Database migrations
│   ├── i18n/                 # Translation infrastructure
│   ├── utils/                # Utilities (security, etc.)
│   ├── main.py               # FastAPI app
│   ├── config.py             # Configuration
│   └── .env                  # Environment variables (create this!)
│
├── js/                       # Frontend JavaScript modules
│   ├── api.js                # API calls
│   ├── auth-guard.js         # Authentication
│   ├── ui.js                 # UI helpers
│   ├── communities.js        # Communities & WebSocket chat
│   └── feed.js               # Posts/feed functionality
│
├── *.html                    # Frontend pages
├── style.css                 # Styling
├── auth.js                   # Legacy auth (being replaced)
├── README.md                 # Full documentation
├── QUICKSTART.md             # This file
└── TESTING_CHECKLIST.md      # Comprehensive test guide
```

---

## ⚙️ Daily Usage

```bash
# 1. Activate venv (always do this first)
cd /path/to/website-file-2
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Start backend server
python3 -m people_help --reload

# 3. In another terminal, serve frontend
python3 -m http.server 5500
```

**Tip**: Keep both terminals open. Use Ctrl+C to stop servers when done.

---

## 🐛 Troubleshooting

### "command not found: python"
Use `python3` instead:
```bash
python3 -m venv venv
```

### "Module 'people_help' has no attribute 'cli'"
You forgot to activate the venv:
```bash
source venv/bin/activate
pip install -e .
```

### "ValueError: SECRET_KEY environment variable is required"
Generate and add SECRET_KEY to `people_help/.env`:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to .env file as SECRET_KEY=...
```

### "Failed to connect to database"
Make sure PostgreSQL is running:
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL (macOS with Homebrew)
brew services start postgresql@14

# Create database if needed
createdb people_help_db
```

### "Port already in use"
Change the backend port:
```bash
python3 -m people_help --port 9000 --reload
```

**Note**: If you change the backend port, update `js/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:9000/api';
```

### "WebSocket connection failed"
1. Check backend is running on port 8888
2. Check browser console for errors
3. Verify you're a member of the community
4. Try refreshing the page

### Frontend not loading / 404 errors
Make sure you're accessing the correct URL:
- ✅ http://localhost:5500/landing.html
- ❌ http://localhost:5500/ (no index.html)

### Database tables missing
Apply migrations manually:
```bash
psql -U postgres -d people_help_db -f people_help/migrations/001_add_language_to_users.sql
psql -U postgres -d people_help_db -f people_help/migrations/002_create_communities_tables.sql
psql -U postgres -d people_help_db -f people_help/migrations/003_create_posts_table.sql
```

---

## 🔐 Security Notes

- **Never commit `.env` file** - it contains secrets!
- SECRET_KEY is required for JWT tokens
- Rate limiting is enabled by default (60 requests/min)
- All user input is sanitized to prevent XSS
- Passwords are hashed with bcrypt

---

## 📚 Next Steps

1. **Read the full documentation**: [README.md](README.md)
2. **Run comprehensive tests**: [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)
3. **Explore the API**: http://localhost:8888/docs
4. **Check migrations**: [people_help/migrations/README.md](people_help/migrations/README.md)

---

## 💡 Key Features

✅ **Authentication**: JWT-based with rate limiting
✅ **Communities**: Join communities and participate
✅ **Real-Time Chat**: WebSocket-based instant messaging
✅ **Feed**: Create, view, and delete posts
✅ **Multi-Language**: Infrastructure ready (English default)
✅ **Responsive**: Works on desktop and mobile
✅ **Secure**: XSS prevention, permission checks, bcrypt passwords

---

## 🆘 Getting Help

- **API Issues**: Check http://localhost:8888/docs
- **Frontend Issues**: Check browser console (F12)
- **Database Issues**: Check `psql -U postgres -l` to list databases
- **Server Issues**: Check terminal output for error messages

---

**Remember**: Always activate the venv with `source venv/bin/activate` before working! 🎯

**Quick check**: If you see `(venv)` in your terminal prompt, you're good to go!
