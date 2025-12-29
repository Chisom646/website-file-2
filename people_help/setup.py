import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to Python path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from people_help.config import db
from people_help.models.role import Role
from sqlalchemy import select


async def initialize_default_roles(session):
    """Initialize default roles in the database"""
    default_roles = [
        {"name": "admin", "description": "Administrator with full access"},
        {"name": "user", "description": "Regular user"},
        {"name": "moderator", "description": "Content moderator"}
    ]

    for role_data in default_roles:
        result = await session.execute(
            select(Role).where(Role.name == role_data["name"])
        )
        existing_role = result.scalar_one_or_none()

        if not existing_role:
            role = Role(**role_data)
            session.add(role)

    await session.commit()


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
        await initialize_default_roles(db.session)
        print("✅ Default roles initialized")

        print("\n🎉 Setup completed successfully!")
        print("You can now start the application with:")
        print("  python -m people_help --reload")

    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(setup_database())