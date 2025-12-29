# Installation Guide

## Quick Start

```bash
# 1. Install the package
pip install -e .
# or: pip3 install -e .
# or: python3 -m pip install -e .

# 2. Run the server
python3 -m people_help --reload

# That's it! The server will run on http://localhost:8888
```

## Detailed Commands

### Installation Methods

All of these work:
```bash
pip install -e .
pip3 install -e .
python3 -m pip install -e .
```

Use `--user` flag if you get permission errors:
```bash
pip3 install -e . --user
```

### Running the Server

**Recommended (always works):**
```bash
python3 -m people_help --reload
```

**Alternative (if PATH is configured):**
```bash
people-help --reload
```

**Full path (if you know where it installed):**
```bash
/Users/davidtimothy/Library/Python/3.14/bin/people-help --reload
```

### Common Options

```bash
# Development mode with auto-reload
python3 -m people_help --reload

# Custom port
python3 -m people_help --port 9000

# Custom host and port
python3 -m people_help --host 127.0.0.1 --port 8080

# Debug logging
python3 -m people_help --reload --log-level debug

# Production mode (multiple workers)
python3 -m people_help --workers 4

# Skip environment validation (not recommended)
python3 -m people_help --no-env-check
```

### View All Options

```bash
python3 -m people_help --help
```

## Troubleshooting

### "command not found: people-help"

Use `python3 -m people_help` instead. This always works regardless of PATH configuration.

### "Module 'people_help' has no attribute 'cli'"

You haven't installed the package yet. Run:
```bash
pip install -e .
```

### "ERROR: File 'setup.py' or 'setup.cfg' not found"

Your pip version is too old. The repo includes a `setup.py` shim for compatibility. Make sure you're in the project root directory when running `pip install -e .`

### Permission denied during installation

Use the `--user` flag:
```bash
pip3 install -e . --user
```

### Missing required environment variables

Create a `.env` file in the `people_help/` directory with:
```bash
DB_HOST=localhost
DB_NAME=people_help_db
SECRET_KEY=<generate-with-secrets>
```

See `people_help/.env.example` for a template.

## What Gets Installed

When you run `pip install -e .`, you get:

1. **Command**: `people-help` (installed to Python's bin directory)
2. **Module**: `people_help` (can run with `python3 -m people_help`)
3. **Dependencies**: All required packages (FastAPI, uvicorn, SQLModel, etc.)

The `-e` flag means "editable mode" - changes to the code take effect immediately without reinstalling.

## Uninstalling

```bash
pip uninstall people-help
```

## Upgrading Dependencies

```bash
pip install -e . --upgrade
```
