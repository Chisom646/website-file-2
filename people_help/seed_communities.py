"""Seed script to create 3 default communities"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from people_help.config import db
from people_help.models.community import Community
from sqlalchemy import select


async def seed_communities():
    """Create 3 default support communities"""
    print("🌱 Seeding default communities...")

    default_communities = [
        {
            "name": "Mental Health Support",
            "description": "A safe space for discussing mental health challenges, coping strategies, and recovery journeys.",
            "is_default": True
        },
        {
            "name": "Abuse Survivors",
            "description": "Support group for survivors of abuse to share experiences and find healing together.",
            "is_default": True
        },
        {
            "name": "General Support",
            "description": "Open community for general support, advice, and encouragement on life's challenges.",
            "is_default": True
        }
    ]

    try:
        db.init()

        for community_data in default_communities:
            # Check if community already exists
            result = await db.session.execute(
                select(Community).where(Community.name == community_data["name"])
            )
            existing = result.scalar_one_or_none()

            if not existing:
                community = Community(**community_data)
                db.session.add(community)
                print(f"✅ Created community: {community_data['name']}")
            else:
                print(f"⏭️  Community already exists: {community_data['name']}")

        await db.session.commit()
        print("\n🎉 Default communities seeded successfully!")

    except Exception as e:
        print(f"❌ Error seeding communities: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(seed_communities())
