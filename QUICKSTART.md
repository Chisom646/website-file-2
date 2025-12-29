# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

**Important**: Always activate the venv before working:
```bash
source venv/bin/activate
```

You'll see `(venv)` in your prompt when activated.

### Step 2: Install Package

```bash
pip install -e .
```

✅ This installs all dependencies and the `people-help` command.

### Step 3: Set Up Environment

```bash
# Copy the example env file
cp people_help/.env.example people_help/.env

# Edit it with your settings
nano people_help/.env
```

**Minimum required settings:**
```env
DB_HOST=localhost
DB_NAME=people_help_db
SECRET_KEY=<generate-with-command-below>
```

**Generate a secure secret key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 4: Create Database

```bash
# Create PostgreSQL database
createdb people_help_db

# Or using psql:
psql -U postgres -c "CREATE DATABASE people_help_db;"
```

### Step 5: Initialize Database

```bash
python people_help/setup.py
```

Expected output:
```
🔄 Setting up database...
✅ Tables created successfully
✅ Default roles initialized
🎉 Setup completed successfully!
```

### Step 6: Start the Server

```bash
# Option A: Using the command directly
people-help --reload

# Option B: Using python module (always works)
python -m people_help --reload
```

The server will start on http://localhost:8888

### Step 7: Serve Frontend

Open a **new terminal** (keep the server running), then:

```bash
cd /path/to/website-file-2
python3 -m http.server 5500
```

### Step 8: Access the Application

Open your browser:
- **Frontend**: http://localhost:5500/landing.html
- **API Docs**: http://localhost:8888/docs
- **API**: http://localhost:8888

---

## Daily Usage

```bash
# 1. Activate venv (always do this first)
cd /path/to/website-file-2
source venv/bin/activate

# 2. Start backend server
python -m people_help --reload

# 3. In another terminal, serve frontend
python3 -m http.server 5500
```

---

## Troubleshooting

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

### "Missing required environment variables"
Create the `.env` file:
```bash
cp people_help/.env.example people_help/.env
# Then edit people_help/.env with your settings
```

### "Failed to connect to database"
Make sure PostgreSQL is running and the database exists:
```bash
# Check if PostgreSQL is running
pg_isready

# Create database if needed
createdb people_help_db
```

### Port already in use
Change the port:
```bash
python -m people_help --port 9000 --reload
```

Don't forget to update `auth.js` if you change the backend port!

---

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [INSTALLATION.md](INSTALLATION.md) for troubleshooting
- Explore the API at http://localhost:8888/docs

---

**Remember**: Always activate the venv with `source venv/bin/activate` before working! 🎯
