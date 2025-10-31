import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ..connection import SessionLocal
from ...services import FAQService

def seed_categories():
    """Seed initial FAQ categories"""
    db = SessionLocal()
    faq_service = FAQService()
    
    try:
        # Check if categories already exist
        existing = faq_service.get_all_faq_categories(db)
        if existing:
            print("Categories already exist. Skipping seed.")
            return
        
        categories_data = [
            {
                "name": "General",
                "slug": "general",
                "description": "General questions and information",
                "icon": "📋",
                "order_index": 1
            },
            {
                "name": "Getting Started",
                "slug": "getting_started",
                "description": "Help for new users getting started",
                "icon": "🚀",
                "order_index": 2
            },
            {
                "name": "Technical Support",
                "slug": "technical",
                "description": "Technical issues and troubleshooting",
                "icon": "🔧",
                "order_index": 3
            },
            {
                "name": "Account",
                "slug": "account",
                "description": "Account management and settings",
                "icon": "👤",
                "order_index": 4
            },
            {
                "name": "Billing",
                "slug": "billing",
                "description": "Billing and payment questions",
                "icon": "💳",
                "order_index": 5
            },
            {
                "name": "Troubleshooting",
                "slug": "troubleshooting",
                "description": "Common problems and solutions",
                "icon": "🔍",
                "order_index": 6
            }
        ]
        
        for cat_data in categories_data:
            faq_service.create_category(
                db=db,
                name=cat_data["name"],
                slug=cat_data["slug"],
                description=cat_data["description"],
                icon=cat_data["icon"],
                is_active=True,
                order_index=cat_data["order_index"]
            )
        
        print(f"✅ Successfully seeded {len(categories_data)} categories!")
        
    except Exception as e:
        print(f"❌ Error seeding categories: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding FAQ categories...")
    seed_categories()
    print("Done!")