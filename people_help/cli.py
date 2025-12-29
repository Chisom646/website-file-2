"""
CLI entry point for People Help The People application.
"""
import argparse
import os
import sys
from pathlib import Path
import uvicorn
from dotenv import load_dotenv


# Load .env file from the people_help directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


def validate_environment():
    """Validate that critical environment variables are set."""
    required_vars = {
        "DB_HOST": "Database host (e.g., localhost)",
        "DB_NAME": "Database name (e.g., people_help_db)",
        "SECRET_KEY": "JWT secret key for token signing",
    }

    missing = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing.append(f"  - {var}: {description}")

    if missing:
        print("❌ ERROR: Missing required environment variables:\n")
        print("\n".join(missing))
        print("\nPlease set these in your .env file or environment.")
        print("See README.md for setup instructions.")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="People Help The People - Mental health support community platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8888")),
        help="Port to bind to (default: 8888, or PORT env var)",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes (development mode)",
    )

    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Log level (default: info)",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1, use >1 for production)",
    )

    parser.add_argument(
        "--no-env-check",
        action="store_true",
        help="Skip environment variable validation (not recommended)",
    )

    args = parser.parse_args()

    # Validate environment unless explicitly skipped
    if not args.no_env_check:
        validate_environment()

    print(f"🚀 Starting People Help The People API server...")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Reload: {args.reload}")
    print(f"   Workers: {args.workers}")
    print(f"   Log Level: {args.log_level}")
    print()
    print(f"📡 API will be available at: http://localhost:{args.port}")
    print(f"📄 API docs available at: http://localhost:{args.port}/docs")
    print()

    # Run uvicorn
    uvicorn.run(
        "people_help.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        workers=args.workers if not args.reload else 1,  # Workers incompatible with reload
    )


if __name__ == "__main__":
    main()
