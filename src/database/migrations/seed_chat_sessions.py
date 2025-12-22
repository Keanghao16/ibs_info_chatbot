"""
Seed Chat Sessions
Creates test chat sessions for development
"""

from sqlalchemy import text
from ..connection import SessionLocal
from ..models import User, Admin, ChatSession, SessionStatus, ChatMessage
from datetime import datetime, timedelta
import random
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def seed_chat_sessions(count=50):
    """Seed random chat sessions"""
    db = SessionLocal()
    
    try:
        print(f"\n{'='*60}")
        print(f"🌱 Starting Chat Sessions Seeding")
        print(f"{'='*60}\n")
        
        # Get all users and admins (remove is_active filter for User)
        users = db.query(User).all()
        admins = db.query(Admin).filter(Admin.is_active == True).all()
        
        if not users:
            print("❌ No users found. Please run seed_users first.")
            return
        
        if not admins:
            print("❌ No active admins found. Please run seed_super_admin first.")
            return
        
        print(f"👥 Found {len(users)} users")
        print(f"👨‍💼 Found {len(admins)} active admins\n")
        
        print(f"🔄 Creating {count} chat sessions...\n")
        
        sessions_created = 0
        
        for i in range(count):
            user = random.choice(users)
            admin = random.choice(admins)
            
            # Random start time within last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            start_time = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
            
            # 70% chance of being closed
            is_closed = random.random() < 0.7
            
            end_time = None
            status = SessionStatus.active
            
            if is_closed:
                # Session duration between 5 minutes and 2 hours
                duration_minutes = random.randint(5, 120)
                end_time = start_time + timedelta(minutes=duration_minutes)
                status = SessionStatus.closed
            
            session = ChatSession(
                user_id=user.id,
                admin_id=admin.id,
                start_time=start_time,
                end_time=end_time,
                status=status
            )
            
            db.add(session)
            sessions_created += 1
            
            if sessions_created % 10 == 0:
                print(f"   Created {sessions_created}/{count} sessions...")
        
        db.commit()
        
        # Get statistics
        total_sessions = db.query(ChatSession).count()
        active_sessions = db.query(ChatSession).filter(
            ChatSession.status == SessionStatus.active
        ).count()
        closed_sessions = db.query(ChatSession).filter(
            ChatSession.status == SessionStatus.closed
        ).count()
        
        print(f"\n{'='*60}")
        print(f" Seeding Complete!")
        print(f"{'='*60}")
        print(f"   Total sessions: {total_sessions}")
        print(f"   Active sessions: {active_sessions}")
        print(f"   Closed sessions: {closed_sessions}")
        print(f"\n{'='*60}\n")
        
        # Show sample sessions
        print("💬 Sample Sessions (last 5 created):")
        print(f"{'='*60}")
        sample_sessions = db.query(ChatSession).order_by(
            ChatSession.start_time.desc()
        ).limit(5).all()
        
        for session in sample_sessions:
            status_icon = "🟢" if session.status == SessionStatus.active else "🔴"
            duration = ""
            if session.end_time:
                delta = session.end_time - session.start_time
                duration = f" ({delta.total_seconds() // 60:.0f} min)"
            
            print(f"\n  {status_icon} Session #{session.id}")
            print(f"     User: {session.user.full_name}")
            print(f"     Admin: {session.admin.full_name}")
            print(f"     Started: {session.start_time.strftime('%Y-%m-%d %H:%M')}")
            if session.end_time:
                print(f"     Ended: {session.end_time.strftime('%Y-%m-%d %H:%M')}{duration}")
        
        print(f"\n{'='*60}")
        
    except Exception as e:
        print(f"\n❌ Error seeding chat sessions: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def clear_all_sessions():
    """Clear all chat sessions"""
    db = SessionLocal()
    
    try:
        count = db.query(ChatSession).count()
        
        if count == 0:
            print("\n📭 No sessions to delete.")
            return
        
        print(f"\n⚠️  WARNING: This will delete all {count} chat sessions!")
        confirm = input("Type 'DELETE' to confirm: ").strip()
        
        if confirm == "DELETE":
            db.query(ChatSession).delete()
            db.commit()
            print(f"\n Successfully deleted {count} chat sessions.")
        else:
            print("\n❌ Deletion cancelled.")
            
    except Exception as e:
        print(f"\n❌ Error clearing sessions: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("💬 IBS Info Chatbot - Chat Sessions Seeder")
    print("=" * 60 + "\n")
    
    # Show current database status
    db = SessionLocal()
    try:
        total = db.query(ChatSession).count()
        active = db.query(ChatSession).filter(
            ChatSession.status == SessionStatus.active
        ).count()
        print(f"📊 Current database status:")
        print(f"   Total sessions: {total}")
        print(f"   Active: {active}")
        print(f"   Closed: {total - active}\n")
    except:
        print("📊 Database status: Unable to connect\n")
    finally:
        db.close()
    
    print("Options:")
    print("1. Add 50 chat sessions")
    print("2. Add 100 chat sessions")
    print("3. Add custom number of sessions")
    print("4. Clear all sessions (⚠️  Dangerous!)")
    print("5. View statistics")
    print("6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        seed_chat_sessions(50)
    elif choice == "2":
        seed_chat_sessions(100)
    elif choice == "3":
        try:
            count = int(input("\nEnter number of sessions to add: "))
            if count > 0 and count <= 500:
                seed_chat_sessions(count)
            elif count > 500:
                print("\n❌ Maximum 500 sessions allowed at once.")
            else:
                print("\n❌ Please enter a positive number.")
        except ValueError:
            print("\n❌ Invalid number.")
    elif choice == "4":
        clear_all_sessions()
    elif choice == "5":
        db = SessionLocal()
        try:
            total = db.query(ChatSession).count()
            active = db.query(ChatSession).filter(
                ChatSession.status == SessionStatus.active
            ).count()
            print(f"\n📊 Database Statistics:")
            print(f"   Total Sessions: {total}")
            print(f"   Active: {active}")
            print(f"   Closed: {total - active}")
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