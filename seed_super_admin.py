from src.database.connection import SessionLocal
from src.services.auth_service import AuthService
from src.database.models import Admin, AdminRole

# def create_initial_super_admin():
#     db = SessionLocal()
#     auth_service = AuthService()
    
#     try:
#         # Create super admin
#         result = auth_service.create_admin(
#             db=db,
#             email="superadmin@gmail.com",  # Change this to your email
#             password="password",             # Change this to a secure password
#             full_name="Super Administrator"
#         )
        
#         if result['success']:
#             # Update role to super_admin
#             admin = db.query(Admin).filter(Admin.email == "superadmin@gmail.com").first()
#             admin.role = AdminRole.super_admin
#             db.commit()
            
#             print("✅ Super admin created successfully!")
#             print("📧 Email: superadmin@gmail.com")
#             print("🔑 Password: password")
#             print("⚠️  Please change these credentials after first login!")
#         else:
#             print(f"❌ Failed to create admin: {result['message']}")
            
#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         db.close()

# def create_test_admin():
#     """Create a test admin (agent) for testing"""
#     db = SessionLocal()
#     auth_service = AuthService()
    
#     try:
#         result = auth_service.create_admin(
#             db=db,
#             email="agent@gmail.com",
#             password="password", 
#             full_name="Test Agent"
#         )
        
#         if result['success']:
#             # Update additional fields for admin role
#             admin = db.query(Admin).filter(Admin.email == "agent@gmail.com").first()
#             admin.telegram_id = "123456789"  # Example Telegram ID
#             admin.division = "Customer Support"
#             admin.role = AdminRole.admin  # This is the agent role
#             admin.is_available = True
#             db.commit()
            
#             print("✅ Test admin/agent created successfully!")
#             print("📧 Email: agent@example.com")
#             print("🔑 Password: agent123")
#             print("👨‍💼 Role: Admin/Agent")
#         else:
#             print(f"❌ Failed to create test admin: {result['message']}")
            
#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         db.close()

def create_telegram_admins():
    db = SessionLocal()
    auth_service = AuthService()
    
    try:
        # Get your actual Telegram ID by messaging @userinfobot
        # Replace YOUR_ACTUAL_TELEGRAM_ID with the real ID
        result1 = auth_service.create_admin_telegram(
            db=db,
            telegram_id="875184794",  # Get this from @userinfobot
            full_name="Super Administrator",
            role="super_admin"
        )
        
        if result1['success']:
            print("✅ Super admin created successfully!")
        else:
            print(f"❌ Failed to create super admin: {result1['message']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # print("Creating initial admin accounts...")
    # create_initial_super_admin()
    # print("\n" + "="*50 + "\n")
    # create_test_admin()
    # print("\n🎉 Setup complete! You can now run the web application.")
    # print("\nCreating Telegram admin accounts...")
    print("Creating initial admin accounts...")
    create_telegram_admins()
    print("\n🎉 Setup complete! You can now run the web application.")
