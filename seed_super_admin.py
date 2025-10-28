from src.database.connection import SessionLocal
from src.database.models import Admin, AdminRole
from datetime import datetime

def create_telegram_super_admin():
    """Create super admin using Telegram ID"""
    db = SessionLocal()
    
    try:
        telegram_id = "875184794"  # Your Telegram ID from @userinfobot
        
        # Check if admin already exists
        existing_admin = db.query(Admin).filter(
            Admin.telegram_id == telegram_id
        ).first()
        
        if existing_admin:
            print(f"⚠️  Admin with Telegram ID {telegram_id} already exists!")
            print(f"📧 Name: {existing_admin.full_name}")
            print(f"🔐 Role: {existing_admin.role.value}")
            return
        
        # Create new super admin
        super_admin = Admin(
            telegram_id=telegram_id,
            full_name="Super Administrator",
            role=AdminRole.super_admin,
            is_active=True,
            is_available=True,
            division="Management",
            created_at=datetime.now()
        )
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print("=" * 60)
        print("✅ Super Admin Created Successfully!")
        print("=" * 60)
        print(f"👤 Name: {super_admin.full_name}")
        print(f"🆔 Telegram ID: {super_admin.telegram_id}")
        print(f"🔐 Role: {super_admin.role.value}")
        print(f"📁 Division: {super_admin.division}")
        print("=" * 60)
        print("\n📱 Next Steps:")
        print("1. Open Telegram and search for your bot")
        print("2. Send /start command to the bot")
        print("3. You'll be recognized as Super Admin")
        print("4. Access admin panel via web interface")
        print("=" * 60)
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating super admin: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def create_test_admin_agent():
    """Create a test admin/agent for testing"""
    db = SessionLocal()
    
    try:
        # Replace with actual Telegram ID for testing
        telegram_id = "123456789"  # Change this!
        
        # Check if admin already exists
        existing_admin = db.query(Admin).filter(
            Admin.telegram_id == telegram_id
        ).first()
        
        if existing_admin:
            print(f"⚠️  Admin with Telegram ID {telegram_id} already exists!")
            return
        
        test_admin = Admin(
            telegram_id=telegram_id,
            telegram_username="test_agent",
            telegram_first_name="Test",
            telegram_last_name="Agent",
            full_name="Test Agent",
            role=AdminRole.admin,  # Regular admin (agent)
            is_active=True,
            is_available=True,
            division="Customer Support",
            created_at=datetime.now()
        )
        
        db.add(test_admin)
        db.commit()
        db.refresh(test_admin)
        
        print("=" * 60)
        print("✅ Test Admin/Agent Created Successfully!")
        print("=" * 60)
        print(f"👤 Name: {test_admin.full_name}")
        print(f"🆔 Telegram ID: {test_admin.telegram_id}")
        print(f"🔐 Role: {test_admin.role.value}")
        print(f"📁 Division: {test_admin.division}")
        print("=" * 60)
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating test admin: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def list_all_admins():
    """List all existing admins"""
    db = SessionLocal()
    
    try:
        admins = db.query(Admin).all()
        
        if not admins:
            print("📭 No admins found in database")
            return
        
        print("\n" + "=" * 60)
        print("📋 Current Admins in Database")
        print("=" * 60)
        
        for admin in admins:
            print(f"\n{'='*60}")
            print(f"👤 Name: {admin.full_name}")
            print(f"🆔 Telegram ID: {admin.telegram_id}")
            if admin.telegram_username:
                print(f"📱 Username: @{admin.telegram_username}")
            print(f"🔐 Role: {admin.role.value}")
            print(f"📁 Division: {admin.division or 'N/A'}")
            print(f"✅ Active: {'Yes' if admin.is_active else 'No'}")
            print(f"🟢 Available: {'Yes' if admin.is_available else 'No'}")
            
    except Exception as e:
        print(f"❌ Error listing admins: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 IBS Info Chatbot - Admin Setup")
    print("=" * 60 + "\n")
    
    # Create super admin
    print("📝 Creating Super Administrator...")
    create_telegram_super_admin()
    
    print("\n" + "=" * 60 + "\n")
    
    # Optionally create test admin (uncomment if needed)
    # print("📝 Creating Test Admin/Agent...")
    # create_test_admin_agent()
    # print("\n" + "=" * 60 + "\n")
    
    # List all admins
    print("📋 Listing all admins...")
    list_all_admins()
    
    print("\n" + "=" * 60)
    print("✨ Setup Complete!")
    print("=" * 60 + "\n")
