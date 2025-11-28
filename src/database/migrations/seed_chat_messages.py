import sys
import os
from datetime import datetime, timedelta
import random

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ..connection import SessionLocal
from ..models import ChatSession, ChatMessage

def generate_sample_messages():
    """Generate sample chat messages"""
    user_messages = [
        "Hello, I need help with my account",
        "Can you help me with billing?",
        "I'm having trouble accessing the service",
        "How do I update my profile?",
        "What are your operating hours?",
        "I need a refund",
        "The system is showing an error",
        "Thank you for your help!",
        "Is there a discount available?",
        "How long will this take?",
        "Can I speak to a manager?",
        "I appreciate your assistance",
        "What's the status of my request?",
        "I need technical support",
        "This is urgent, please help"
    ]
    
    admin_messages = [
        "Hello! How can I assist you today?",
        "I'd be happy to help you with that.",
        "Let me check that for you.",
        "I understand your concern.",
        "Can you provide more details?",
        "I've processed your request.",
        "Is there anything else I can help with?",
        "Thank you for your patience.",
        "Your issue has been resolved.",
        "I've sent the information to your email.",
        "Let me transfer you to the right department.",
        "I'll escalate this to management.",
        "Your account has been updated.",
        "You're all set now!",
        "Feel free to reach out anytime."
    ]
    
    return user_messages, admin_messages

def seed_chat_messages(messages_per_session=5):
    """Seed random chat messages for existing sessions"""
    db = SessionLocal()
    
    try:
        print(f"\n{'='*60}")
        print(f"💬 Starting Chat Messages Seeding")
        print(f"{'='*60}\n")
        
        # Get all sessions
        sessions = db.query(ChatSession).all()
        
        if not sessions:
            print("❌ No chat sessions found. Please run seed_chat_sessions first.")
            return
        
        print(f"📊 Found {len(sessions)} chat sessions")
        print(f"📝 Creating ~{messages_per_session} messages per session\n")
        
        user_messages, admin_messages = generate_sample_messages()
        
        total_messages = 0
        
        for session in sessions:
            # Random number of messages per session
            num_messages = random.randint(2, messages_per_session * 2)
            
            # Start time for messages
            current_time = session.start_time
            
            # Add initial greeting from admin
            message = ChatMessage(
                session_id=session.id,
                user_id=session.user_id,
                admin_id=session.admin_id,
                is_from_admin=True,  # ✅ Changed from sender_type
                message=random.choice(admin_messages),  # ✅ Changed from message_text
                timestamp=current_time  # ✅ Changed from sent_at
            )
            db.add(message)
            total_messages += 1
            
            # Add conversation messages
            for i in range(num_messages):
                # Alternate between user and admin messages
                is_from_admin = (i % 2) != 0  # ✅ Changed logic
                
                # Add 1-5 minutes between messages
                current_time += timedelta(minutes=random.randint(1, 5))
                
                # Don't exceed session end time if closed
                if session.end_time and current_time > session.end_time:
                    break
                
                message_text = random.choice(
                    admin_messages if is_from_admin else user_messages
                )
                
                message = ChatMessage(
                    session_id=session.id,
                    user_id=session.user_id,
                    admin_id=session.admin_id,
                    is_from_admin=is_from_admin,  # ✅ Changed from sender_type
                    message=message_text,  # ✅ Changed from message_text
                    timestamp=current_time  # ✅ Changed from sent_at
                )
                db.add(message)
                total_messages += 1
            
            if total_messages % 50 == 0:
                print(f"   Created {total_messages} messages...")
        
        db.commit()
        
        # Get statistics
        total_in_db = db.query(ChatMessage).count()
        user_msg_count = db.query(ChatMessage).filter(
            ChatMessage.is_from_admin == False  # ✅ Changed from sender_type
        ).count()
        admin_msg_count = db.query(ChatMessage).filter(
            ChatMessage.is_from_admin == True  # ✅ Changed from sender_type
        ).count()
        
        print(f"\n{'='*60}")
        print(f"✅ Seeding Complete!")
        print(f"{'='*60}")
        print(f"   Total messages: {total_in_db}")
        print(f"   User messages: {user_msg_count}")
        print(f"   Admin messages: {admin_msg_count}")
        print(f"\n{'='*60}\n")
        
        # Show sample messages
        print("💬 Sample Messages (last 10 created):")
        print(f"{'='*60}")
        sample_messages = db.query(ChatMessage).order_by(
            ChatMessage.timestamp.desc()  # ✅ Changed from sent_at
        ).limit(10).all()
        
        for msg in sample_messages:
            icon = "👨‍💼" if msg.is_from_admin else "👤"  # ✅ Changed from sender_type
            sender = msg.admin.full_name if msg.is_from_admin else msg.user.full_name
            
            print(f"\n  {icon} {sender}")
            print(f"     {msg.message[:60]}...")  # ✅ Changed from message_text
            print(f"     🕒 {msg.timestamp.strftime('%Y-%m-%d %H:%M')}")  # ✅ Changed from sent_at
        
        print(f"\n{'='*60}")
        
    except Exception as e:
        print(f"\n❌ Error seeding chat messages: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def clear_all_messages():
    """Clear all chat messages"""
    db = SessionLocal()
    
    try:
        count = db.query(ChatMessage).count()
        
        if count == 0:
            print("\n📭 No messages to delete.")
            return
        
        print(f"\n⚠️  WARNING: This will delete all {count} chat messages!")
        confirm = input("Type 'DELETE' to confirm: ").strip()
        
        if confirm == "DELETE":
            db.query(ChatMessage).delete()
            db.commit()
            print(f"\n✅ Successfully deleted {count} chat messages.")
        else:
            print("\n❌ Deletion cancelled.")
            
    except Exception as e:
        print(f"\n❌ Error clearing messages: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("💬 IBS Info Chatbot - Chat Messages Seeder")
    print("=" * 60 + "\n")
    
    # Show current database status
    db = SessionLocal()
    try:
        total = db.query(ChatMessage).count()
        user_msgs = db.query(ChatMessage).filter(
            ChatMessage.is_from_admin == False  # ✅ Changed from sender_type
        ).count()
        admin_msgs = db.query(ChatMessage).filter(
            ChatMessage.is_from_admin == True  # ✅ Changed from sender_type
        ).count()
        print(f"📊 Current database status:")
        print(f"   Total messages: {total}")
        print(f"   User messages: {user_msgs}")
        print(f"   Admin messages: {admin_msgs}\n")
    except:
        print("📊 Database status: Unable to connect\n")
    finally:
        db.close()
    
    print("Options:")
    print("1. Seed messages (5 per session)")
    print("2. Seed messages (10 per session)")
    print("3. Custom messages per session")
    print("4. Clear all messages (⚠️  Dangerous!)")
    print("5. View statistics")
    print("6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        seed_chat_messages(5)
    elif choice == "2":
        seed_chat_messages(10)
    elif choice == "3":
        try:
            count = int(input("\nEnter messages per session: "))
            if count > 0 and count <= 50:
                seed_chat_messages(count)
            else:
                print("\n❌ Please enter 1-50.")
        except ValueError:
            print("\n❌ Invalid number.")
    elif choice == "4":
        clear_all_messages()
    elif choice == "5":
        db = SessionLocal()
        try:
            total = db.query(ChatMessage).count()
            user_msgs = db.query(ChatMessage).filter(
                ChatMessage.is_from_admin == False
            ).count()
            admin_msgs = db.query(ChatMessage).filter(
                ChatMessage.is_from_admin == True
            ).count()
            print(f"\n📊 Database Statistics:")
            print(f"   Total Messages: {total}")
            print(f"   User Messages: {user_msgs}")
            print(f"   Admin Messages: {admin_msgs}")
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