import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from config import db
from services.auth_service import initialize_default_roles


async def setup_database():
    """Initialize database and create default data"""
    print("🔄 Setting up database...")
    
    try:
        # Initialize database connection
        db.init()
        
        # Create all tables
        await db.create_all()
        print("✅ Tables created successfully")
        
        # Initialize default roles
        async with db.session() as session:
            await initialize_default_roles(session)
        print("✅ Default roles initialized")
        
        print("\n🎉 Setup completed successfully!")
        print("You can now start the application with:")
        print("  uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(setup_database())