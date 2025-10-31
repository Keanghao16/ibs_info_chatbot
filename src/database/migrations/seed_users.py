import sys
import os
from datetime import datetime, timedelta
import random
import uuid

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
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
        "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts"
    ]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    # Use timestamp to make username more unique
    timestamp = int(datetime.utcnow().timestamp() * 1000) % 10000
    username = f"{first_name.lower()}{last_name.lower()}{timestamp}{random.randint(1, 999)}"
    full_name = f"{first_name} {last_name}"
    
    # Generate more unique telegram_id using timestamp
    telegram_id = str(1000000000 + index * 1000 + random.randint(100, 999))
    
    # Random creation date within last 6 months
    days_ago = random.randint(1, 180)
    created_at = datetime.utcnow() - timedelta(days=days_ago)
    
    # 90% chance of being active
    is_active = random.random() < 0.9
    
    # Optional photo URL (50% chance)
    photo_url = None
    if random.random() < 0.5:
        photo_url = f"https://i.pravatar.cc/150?img={random.randint(1, 70)}"
    
    return {
        'id': str(uuid.uuid4()),
        'telegram_id': telegram_id,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'full_name': full_name,
        'photo_url': photo_url,
        'is_active': is_active,
        'created_at': created_at
    }

def seed_users(count=100):
    """Seed random users"""
    db = SessionLocal()
    
    try:
        # Get current count
        existing_count = db.query(User).count()
        
        if existing_count > 0:
            print(f"ℹ️  Database currently has {existing_count} users.")
            print(f"   Adding {count} more users...\n")
        else:
            print(f"📝 Starting fresh. Creating {count} users...\n")
        
        users_added = 0
        users_to_add = []
        
        print(f"🔄 Generating users...")
        
        for i in range(count * 2):  # Generate more than needed to account for duplicates
            if users_added >= count:
                break
                
            user_data = generate_random_user(i)
            
            # Check if telegram_id already exists in database
            existing = db.query(User).filter(
                User.telegram_id == user_data['telegram_id']
            ).first()
            
            # Also check if it's already in our batch to add
            duplicate_in_batch = any(u.telegram_id == user_data['telegram_id'] for u in users_to_add)
            
            if not existing and not duplicate_in_batch:
                new_user = User(**user_data)
                users_to_add.append(new_user)
                users_added += 1
                
                if users_added % 10 == 0:
                    print(f"  ✓ Prepared {users_added}/{count} users...")
        
        if len(users_to_add) == 0:
            print("\n⚠️  Could not generate any new unique users.")
            print("   Try clearing the database first with option 3.")
            return
        
        # Insert users
        print(f"\n💾 Inserting {len(users_to_add)} users into database...")
        
        # Add one by one for better error handling
        success_count = 0
        for user in users_to_add:
            try:
                db.add(user)
                db.commit()
                success_count += 1
                
                if success_count % 20 == 0:
                    print(f"  ✓ Inserted {success_count}/{len(users_to_add)} users...")
            except Exception as e:
                print(f"  ⚠️  Skipped duplicate: {user.telegram_id}")
                db.rollback()
                continue
        
        print(f"\n{'='*60}")
        print(f"✅ Successfully added {success_count} users!")
        print(f"{'='*60}\n")
        
        # Display statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        inactive_users = total_users - active_users
        
        print("📊 Database Statistics:")
        print(f"   Total Users: {total_users}")
        print(f"   Active Users: {active_users} ({(active_users/total_users*100):.1f}%)")
        print(f"   Inactive Users: {inactive_users} ({(inactive_users/total_users*100):.1f}%)")
        print(f"\n{'='*60}\n")
        
        # Show sample users
        print("👥 Sample Users (last 5 added):")
        print(f"{'='*60}")
        sample_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
        for user in sample_users:
            status = "🟢 Active" if user.is_active else "🔴 Inactive"
            
            print(f"\n  Name: {user.full_name}")
            print(f"  Username: @{user.username}")
            print(f"  Telegram ID: {user.telegram_id}")
            print(f"  Status: {status}")
            print(f"  Created: {user.created_at.strftime('%Y-%m-%d')}")
                
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
        print(f"⚠️  This action cannot be undone!")
        confirm = input("\nType 'DELETE' to confirm: ")
        
        if confirm == "DELETE":
            print("\n🗑️  Deleting users...")
            db.query(User).delete()
            db.commit()
            print(f"✅ Successfully deleted {count} users.")
        else:
            print("\n❌ Operation cancelled.")
    
    except Exception as e:
        print(f"\n❌ Error clearing users: {e}")
        import traceback
        traceback.print_exc()
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
        print(f"📊 Current database status: {current_count} users\n")
    except:
        print("📊 Database status: Unknown\n")
    finally:
        db.close()
    
    print("Options:")
    print("1. Add 100 users")
    print("2. Add custom number of users")
    print("3. Clear all users (⚠️  Dangerous!)")
    print("4. View database stats")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        print("\n" + "=" * 60)
        seed_users(100)
    elif choice == "2":
        try:
            count = int(input("\nEnter number of users to add: "))
            if count > 0 and count <= 1000:
                print("\n" + "=" * 60)
                seed_users(count)
            elif count > 1000:
                print("\n❌ Maximum 1000 users allowed at once.")
            else:
                print("\n❌ Please enter a positive number.")
        except ValueError:
            print("\n❌ Invalid number. Please enter a valid integer.")
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user.")
    elif choice == "3":
        clear_all_users()
    elif choice == "4":
        db = SessionLocal()
        try:
            total = db.query(User).count()
            active = db.query(User).filter(User.is_active == True).count()
            print(f"\n📊 Database Statistics:")
            print(f"   Total Users: {total}")
            print(f"   Active: {active}")
            print(f"   Inactive: {total - active}")
        finally:
            db.close()
    elif choice == "5":
        print("\n👋 Goodbye!")
        return
    else:
        print("\n❌ Invalid choice. Please select 1-5.")
    
    print("\n" + "=" * 60)
    print("✨ Done!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        print("\n" + "=" * 60)
        print("✨ Exiting...")
        print("=" * 60 + "\n")