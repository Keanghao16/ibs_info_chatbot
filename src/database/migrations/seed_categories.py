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
        print("\n" + "=" * 60)
        print("🌱 Starting FAQ Categories Seeding")
        print("=" * 60 + "\n")
        
        # Check if categories already exist
        existing = faq_service.get_all_faq_categories(db)
        if existing:
            print(f"ℹ️  Categories already exist ({len(existing)} found).")
            print("   Skipping seed process.\n")
            
            # Display existing categories
            print("📁 Existing Categories:")
            for cat in existing:
                status = "🟢" if cat.is_active else "🔴"
                print(f"   {status} {cat.icon} {cat.name} ({cat.slug})")
            
            print("\n" + "=" * 60)
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
        
        print(f"📝 Creating {len(categories_data)} categories...\n")
        
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
            print(f"   ✅ Created: {cat_data['icon']} {cat_data['name']}")
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully seeded {len(categories_data)} categories!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error seeding categories: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def clear_categories():
    """Clear all categories"""
    db = SessionLocal()
    faq_service = FAQService()
    
    try:
        categories = faq_service.get_all_faq_categories(db)
        
        if not categories:
            print("\n📭 No categories to delete.")
            return
        
        print(f"\n⚠️  WARNING: This will delete all {len(categories)} categories!")
        print("   This may also affect associated FAQs.\n")
        confirm = input("Type 'DELETE' to confirm: ").strip()
        
        if confirm == "DELETE":
            from ..models import FAQCategory
            db.query(FAQCategory).delete()
            db.commit()
            print(f"\n✅ Successfully deleted {len(categories)} categories.")
        else:
            print("\n❌ Deletion cancelled.")
            
    except Exception as e:
        print(f"\n❌ Error clearing categories: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main menu"""
    print("\n" + "=" * 60)
    print("🗂️  IBS Info Chatbot - FAQ Categories Manager")
    print("=" * 60 + "\n")
    
    db = SessionLocal()
    faq_service = FAQService()
    try:
        existing = faq_service.get_all_faq_categories(db)
        print(f"📊 Current status: {len(existing)} categories in database\n")
    finally:
        db.close()
    
    print("Options:")
    print("1. Seed Categories")
    print("2. Clear All Categories")
    print("3. View Categories")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        seed_categories()
    elif choice == "2":
        clear_categories()
    elif choice == "3":
        db = SessionLocal()
        faq_service = FAQService()
        try:
            categories = faq_service.get_all_faq_categories(db)
            if categories:
                print("\n📁 FAQ Categories:")
                for cat in categories:
                    status = "🟢" if cat.is_active else "🔴"
                    print(f"   {status} {cat.icon} {cat.name} ({cat.slug})")
                    print(f"      {cat.description}")
            else:
                print("\n📭 No categories found.")
        finally:
            db.close()
    elif choice == "4":
        print("\n👋 Goodbye!")
    else:
        print("\n❌ Invalid choice.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")