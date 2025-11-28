import sys
import os
from datetime import datetime, timedelta
import random

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ..connection import SessionLocal
from ..models import User

def generate_random_user(index):
    """Generate random user data"""
    
    # Sample first names
    first_names = [
        "John", "Jane", "Michael", "Sarah", "David", "Emma", "James", "Olivia",
        "Robert", "Sophia", "William", "Isabella", "Richard", "Mia", "Joseph",
        "Charlotte", "Thomas", "Amelia", "Christopher", "Harper", "Daniel", "Evelyn",
        "Matthew", "Abigail", "Anthony", "Emily", "Donald", "Elizabeth", "Mark",
        "Sofia", "Steven", "Avery", "Andrew", "Ella", "Joshua", "Madison", "Kenneth",
        "Scarlett", "Kevin", "Victoria", "Brian", "Aria", "George", "Grace", "Edward",
        "Chloe", "Ronald", "Camila", "Timothy", "Penelope", "Jason", "Riley"
    ]
    
    # Sample last names
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
    ]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    # Use timestamp to make username more unique
    timestamp = int(datetime.utcnow().timestamp() * 1000) % 10000
    username = f"{first_name.lower()}{last_name.lower()}{timestamp}{random.randint(1, 999)}"
    
    # Generate more unique telegram_id using timestamp
    telegram_id = 1000000000 + index * 1000 + random.randint(100, 999)
    
    # Random registration date within last 6 months
    days_ago = random.randint(1, 180)
    registration_date = datetime.utcnow() - timedelta(days=days_ago)
    
    # Random last activity (within last 30 days for active users)
    last_activity_days = random.randint(1, 30)
    last_activity = datetime.utcnow() - timedelta(days=last_activity_days)
    
    # Random language code
    languages = ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko"]
    language_code = random.choice(languages)
    
    # 10% chance of being premium
    is_premium = random.random() < 0.1
    
    return {
        'telegram_id': telegram_id,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'language_code': language_code,
        'is_bot': False,
        'is_premium': is_premium,
        'registration_date': registration_date,
        'last_activity': last_activity
    }

def seed_users(count=100):
    """Seed random users"""
    db = SessionLocal()
    
    try:
        # Get current count
        existing_count = db.query(User).count()
        
        print(f"\n{'='*60}")
        print(f"🌱 Starting User Seeding Process")
        print(f"{'='*60}\n")
        
        if existing_count > 0:
            print(f"ℹ️  Database currently has {existing_count} users.")
            print(f"   Adding {count} more users...\n")
        else:
            print(f"📝 Starting fresh. Creating {count} users...\n")
        
        users_added = 0
        users_to_add = []
        
        print(f"🔄 Generating users...")
        
        for i in range(count * 3):  # Generate more to account for duplicates
            if users_added >= count:
                break
                
            user_data = generate_random_user(i)
            
            # Check if telegram_id already exists
            existing = db.query(User).filter(
                User.telegram_id == user_data['telegram_id']
            ).first()
            
            # Check if it's already in our batch
            duplicate_in_batch = any(u['telegram_id'] == user_data['telegram_id'] for u in users_to_add)
            
            if not existing and not duplicate_in_batch:
                users_to_add.append(user_data)
                users_added += 1
                
                if users_added % 10 == 0:
                    print(f"   Generated {users_added}/{count} users...")
        
        if len(users_to_add) < count:
            print(f"\n⚠️  Could only generate {len(users_to_add)} unique users")
        
        # Bulk insert
        print(f"\n💾 Inserting {len(users_to_add)} users into database...")
        
        for user_data in users_to_add:
            user = User(**user_data)
            db.add(user)
        
        db.commit()
        
        # Get final count
        final_count = db.query(User).count()
        
        print(f"\n{'='*60}")
        print(f"✅ Seeding Complete!")
        print(f"{'='*60}")
        print(f"   Total users in database: {final_count}")
        print(f"   Users added this run: {len(users_to_add)}")
        print(f"\n{'='*60}\n")
        
        # Show sample users
        print("👥 Sample Users (last 5 added):")
        print(f"{'='*60}")
        sample_users = db.query(User).order_by(User.registration_date.desc()).limit(5).all()
        for user in sample_users:
            premium = "👑 Premium" if user.is_premium else "🆓 Free"
            
            print(f"\n  Name: {user.full_name}")
            print(f"  Username: @{user.username}")
            print(f"  Telegram ID: {user.telegram_id}")
            print(f"  Status: {premium}")
            print(f"  Registered: {user.registration_date.strftime('%Y-%m-%d')}")
            print(f"  Language: {user.language_code}")
                
        print(f"\n{'='*60}")
        
    except Exception as e:
        print(f"\n❌ Error seeding users: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def clear_all_users():
    """Clear all users from database (use with caution!)"""
    db = SessionLocal()
    
    try:
        count = db.query(User).count()
        
        if count == 0:
            print("\n📭 No users to delete.")
            return
        
        print(f"\n⚠️  WARNING: This will delete all {count} users!")
        confirm = input("Type 'DELETE' to confirm: ").strip()
        
        if confirm == "DELETE":
            db.query(User).delete()
            db.commit()
            print(f"\n✅ Successfully deleted {count} users.")
        else:
            print("\n❌ Deletion cancelled.")
            
    except Exception as e:
        print(f"\n❌ Error clearing users: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("🌱 IBS Info Chatbot - User Seeder")
    print("=" * 60 + "\n")
    
    # Show current database status
    db = SessionLocal()
    try:
        current_count = db.query(User).count()
        premium_count = db.query(User).filter(User.is_premium == True).count()
        print(f"📊 Current database status:")
        print(f"   Total users: {current_count}")
        print(f"   Premium users: {premium_count}")
        print(f"   Free users: {current_count - premium_count}\n")
    except:
        print("📊 Database status: Unable to connect\n")
    finally:
        db.close()
    
    print("Options:")
    print("1. Add 100 users")
    print("2. Add 500 users")
    print("3. Add custom number of users")
    print("4. Clear all users (⚠️  Dangerous!)")
    print("5. View database stats")
    print("6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        seed_users(100)
    elif choice == "2":
        seed_users(500)
    elif choice == "3":
        try:
            count = int(input("\nEnter number of users to add: "))
            if count > 0 and count <= 1000:
                seed_users(count)
            elif count > 1000:
                print("\n❌ Maximum 1000 users allowed at once.")
            else:
                print("\n❌ Please enter a positive number.")
        except ValueError:
            print("\n❌ Invalid number. Please enter a valid integer.")
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user.")
    elif choice == "4":
        clear_all_users()
    elif choice == "5":
        db = SessionLocal()
        try:
            total = db.query(User).count()
            premium = db.query(User).filter(User.is_premium == True).count()
            print(f"\n📊 Database Statistics:")
            print(f"   Total Users: {total}")
            print(f"   Premium: {premium}")
            print(f"   Free: {total - premium}")
        finally:
            db.close()
    elif choice == "6":
        print("\n👋 Goodbye!")
    else:
        print("\n❌ Invalid choice.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        print("\n" + "=" * 60)
        print("✨ Exiting...")
        print("=" * 60 + "\n")