import sys
import os
from datetime import datetime
import random

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ..connection import SessionLocal
from ..models import Admin, AdminRole

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
            return existing_admin
        
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
        
        return super_admin
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating super admin: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def create_custom_admin_agent():
    """Create a custom admin/agent with user input"""
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 60)
        print("🎨 Custom Admin/Agent Creator")
        print("=" * 60 + "\n")
        
        # Telegram ID options
        print("Telegram ID Options:")
        print("1. Generate random Telegram ID")
        print("2. Enter custom Telegram ID")
        
        telegram_choice = input("\nChoose option (1-2): ").strip()
        
        if telegram_choice == "1":
            # Generate random Telegram ID
            telegram_id = str(random.randint(1000000000, 9999999999))
            print(f"\n✨ Generated Random Telegram ID: {telegram_id}")
        elif telegram_choice == "2":
            telegram_id = input("\n📱 Enter Telegram ID: ").strip()
            if not telegram_id:
                print("❌ Telegram ID cannot be empty!")
                return None
        else:
            print("❌ Invalid choice!")
            return None
        
        # Check if admin already exists
        existing_admin = db.query(Admin).filter(
            Admin.telegram_id == telegram_id
        ).first()
        
        if existing_admin:
            print(f"\n⚠️  Admin with Telegram ID {telegram_id} already exists!")
            print(f"📧 Name: {existing_admin.full_name}")
            print(f"🔐 Role: {existing_admin.role.value}")
            return existing_admin
        
        # Full Name
        full_name = input("\n👤 Enter Full Name (e.g., John Doe): ").strip()
        if not full_name:
            print("❌ Full name cannot be empty!")
            return None
        
        # Role
        print("\n🔐 Select Role:")
        print("1. Admin/Agent (regular admin)")
        print("2. Super Administrator")
        
        role_choice = input("\nChoose role (1-2): ").strip()
        
        if role_choice == "1":
            role = AdminRole.admin
            role_name = "Admin/Agent"
        elif role_choice == "2":
            role = AdminRole.super_admin
            role_name = "Super Administrator"
        else:
            print("❌ Invalid role choice!")
            return None
        
        # Division (only for admin role)
        division = None
        if role == AdminRole.admin:
            print("\n📁 Enter Division/Department:")
            print("   Examples: Customer Support, Sales, Technical Support, Billing")
            division = input("   Division: ").strip()
            if not division:
                division = "General Support"
        
        # Username (optional)
        telegram_username = input("\n📧 Enter Telegram Username (optional, without @): ").strip() or None
        
        # First Name (optional)
        telegram_first_name = input("👤 Enter Telegram First Name (optional): ").strip() or None
        
        # Last Name (optional)
        telegram_last_name = input("👤 Enter Telegram Last Name (optional): ").strip() or None
        
        # Availability (for admin role)
        is_available = True
        if role == AdminRole.admin:
            available_input = input("\n📞 Is available for chats? (yes/no, default: yes): ").strip().lower()
            is_available = available_input != 'no'
        
        # Confirmation
        print("\n" + "=" * 60)
        print("📋 Admin/Agent Summary:")
        print("=" * 60)
        print(f"👤 Full Name: {full_name}")
        print(f"🆔 Telegram ID: {telegram_id}")
        print(f"🔐 Role: {role_name}")
        if telegram_username:
            print(f"📧 Username: @{telegram_username}")
        if telegram_first_name or telegram_last_name:
            print(f"📛 Telegram Name: {telegram_first_name or ''} {telegram_last_name or ''}")
        if division:
            print(f"📁 Division: {division}")
        if role == AdminRole.admin:
            print(f"📞 Available: {'Yes' if is_available else 'No'}")
        print("=" * 60)
        
        confirm = input("\n✅ Create this admin/agent? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("\n❌ Admin/agent creation cancelled.")
            return None
        
        # Create admin
        new_admin = Admin(
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            telegram_first_name=telegram_first_name,
            telegram_last_name=telegram_last_name,
            full_name=full_name,
            role=role,
            is_active=True,
            is_available=is_available if role == AdminRole.admin else None,
            division=division,
            created_at=datetime.now()
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        print("\n" + "=" * 60)
        print("✅ Admin/Agent Created Successfully!")
        print("=" * 60)
        print(f"👤 Name: {new_admin.full_name}")
        print(f"🆔 Telegram ID: {new_admin.telegram_id}")
        print(f"🔐 Role: {new_admin.role.value}")
        if new_admin.division:
            print(f"📁 Division: {new_admin.division}")
        if role == AdminRole.admin:
            print(f"📞 Available: {'Yes' if new_admin.is_available else 'No'}")
        print("=" * 60)
        
        return new_admin
            
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating admin/agent: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def create_bulk_test_agents(count=5):
    """Create multiple test agents with random data"""
    db = SessionLocal()
    
    try:
        print(f"\n{'='*60}")
        print(f"🌱 Bulk Admin/Agent Creator")
        print(f"{'='*60}\n")
        
        # Sample data
        first_names = ["John", "Jane", "Mike", "Sarah", "David", "Emma", "James", "Lisa", "Robert", "Mary"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Wilson", "Moore"]
        divisions = ["Customer Support", "Sales", "Technical Support", "Billing", "Operations", "General Support"]
        
        agents_created = 0
        
        print(f"🔄 Creating {count} test agents...\n")
        
        for i in range(count):
            # Generate random data
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            full_name = f"{first_name} {last_name}"
            
            # Generate unique telegram_id
            telegram_id = str(random.randint(1000000000, 9999999999))
            
            # Check if already exists
            existing = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
            if existing:
                continue
            
            username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
            division = random.choice(divisions)
            is_available = random.choice([True, True, True, False])  # 75% available
            
            # Create agent
            agent = Admin(
                telegram_id=telegram_id,
                telegram_username=username,
                telegram_first_name=first_name,
                telegram_last_name=last_name,
                full_name=full_name,
                role=AdminRole.admin,
                is_active=True,
                is_available=is_available,
                division=division,
                created_at=datetime.now()
            )
            
            db.add(agent)
            agents_created += 1
            
            if agents_created % 10 == 0:
                print(f"   Created {agents_created}/{count} agents...")
        
        db.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ Bulk Creation Complete!")
        print(f"{'='*60}")
        print(f"   Total agents created: {agents_created}")
        print(f"\n{'='*60}\n")
        
        # Show sample agents
        print("👥 Sample Agents (last 5 created):")
        print(f"{'='*60}")
        sample_agents = db.query(Admin).filter(
            Admin.role == AdminRole.admin
        ).order_by(Admin.created_at.desc()).limit(5).all()
        
        for agent in sample_agents:
            status = "🟢" if agent.is_available else "🔴"
            print(f"\n  {status} {agent.full_name}")
            print(f"     🆔 Telegram ID: {agent.telegram_id}")
            print(f"     📁 Division: {agent.division}")
            print(f"     📧 Username: @{agent.telegram_username}")
        
        print(f"\n{'='*60}")
        
    except Exception as e:
        print(f"\n❌ Error creating bulk agents: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def list_all_admins():
    """List all existing admins"""
    db = SessionLocal()
    
    try:
        admins = db.query(Admin).all()
        
        if not admins:
            print("\n📭 No admins found in database.")
            return
        
        print("\n" + "=" * 60)
        print(f"👥 All Admins ({len(admins)} total)")
        print("=" * 60)
        
        # Separate by role
        super_admins = [a for a in admins if a.role == AdminRole.super_admin]
        agents = [a for a in admins if a.role == AdminRole.admin]
        
        if super_admins:
            print("\n👑 SUPER ADMINISTRATORS:")
            print("-" * 60)
            for admin in super_admins:
                status = "🟢" if admin.is_active else "🔴"
                print(f"\n{status} {admin.full_name}")
                print(f"   🆔 Telegram ID: {admin.telegram_id}")
                print(f"   📅 Created: {admin.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        if agents:
            print("\n\n👨‍💼 ADMINS/AGENTS:")
            print("-" * 60)
            for admin in agents:
                status = "🟢" if admin.is_active else "🔴"
                available = "✅" if admin.is_available else "❌"
                
                print(f"\n{status} {admin.full_name}")
                print(f"   🆔 Telegram ID: {admin.telegram_id}")
                print(f"   📁 Division: {admin.division or 'N/A'}")
                print(f"   📞 Available: {available}")
                print(f"   📅 Created: {admin.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        print("\n" + "=" * 60)
        print(f"📊 Summary:")
        print(f"   Super Admins: {len(super_admins)}")
        print(f"   Admins/Agents: {len(agents)}")
        print(f"   Total: {len(admins)}")
        print("=" * 60)
            
    except Exception as e:
        print(f"❌ Error listing admins: {e}")
    finally:
        db.close()

def delete_admin():
    """Delete an admin by Telegram ID"""
    db = SessionLocal()
    
    try:
        telegram_id = input("\nEnter Telegram ID to delete: ").strip()
        
        admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
        
        if not admin:
            print(f"\n❌ No admin found with Telegram ID: {telegram_id}")
            return
        
        print(f"\n⚠️  About to delete:")
        print(f"   Name: {admin.full_name}")
        print(f"   Role: {admin.role.value}")
        if admin.division:
            print(f"   Division: {admin.division}")
        
        confirm = input("\nType 'DELETE' to confirm: ").strip()
        
        if confirm == "DELETE":
            db.delete(admin)
            db.commit()
            print(f"\n✅ Successfully deleted admin: {admin.full_name}")
        else:
            print("\n❌ Deletion cancelled.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting admin: {e}")
    finally:
        db.close()

def clear_all_agents():
    """Clear all agents (keep super admins)"""
    db = SessionLocal()
    
    try:
        agents = db.query(Admin).filter(Admin.role == AdminRole.admin).all()
        
        if not agents:
            print("\n📭 No agents to delete.")
            return
        
        print(f"\n⚠️  WARNING: This will delete all {len(agents)} agents!")
        print("   Super administrators will be kept.")
        confirm = input("Type 'DELETE' to confirm: ").strip()
        
        if confirm == "DELETE":
            db.query(Admin).filter(Admin.role == AdminRole.admin).delete()
            db.commit()
            print(f"\n✅ Successfully deleted {len(agents)} agents.")
        else:
            print("\n❌ Deletion cancelled.")
            
    except Exception as e:
        print(f"\n❌ Error clearing agents: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main menu"""
    print("\n" + "=" * 60)
    print("🚀 IBS Info Chatbot - Admin Management")
    print("=" * 60 + "\n")
    
    # Show current database status
    db = SessionLocal()
    try:
        total_admins = db.query(Admin).count()
        super_admins = db.query(Admin).filter(Admin.role == AdminRole.super_admin).count()
        agents = db.query(Admin).filter(Admin.role == AdminRole.admin).count()
        available_agents = db.query(Admin).filter(
            Admin.role == AdminRole.admin,
            Admin.is_available == True
        ).count()
        
        print(f"📊 Current database status:")
        print(f"   Total Admins: {total_admins}")
        print(f"   Super Admins: {super_admins}")
        print(f"   Agents: {agents} ({available_agents} available)")
        print()
    except:
        print("📊 Database status: Unable to connect\n")
    finally:
        db.close()
    
    print("Options:")
    print("1. Create Super Admin")
    print("2. Create Custom Admin/Agent (Interactive)")
    print("3. Create Bulk Test Agents")
    print("4. List All Admins")
    print("5. Delete Admin")
    print("6. Clear All Agents (Keep Super Admins)")
    print("7. Exit")
    
    choice = input("\nEnter your choice (1-7): ").strip()
    
    if choice == "1":
        print("\n📝 Creating Super Administrator...")
        create_telegram_super_admin()
    elif choice == "2":
        create_custom_admin_agent()
    elif choice == "3":
        try:
            count = int(input("\nHow many test agents to create? (1-50): "))
            if count > 0 and count <= 50:
                create_bulk_test_agents(count)
            else:
                print("\n❌ Please enter a number between 1 and 50.")
        except ValueError:
            print("\n❌ Invalid number.")
    elif choice == "4":
        list_all_admins()
    elif choice == "5":
        delete_admin()
    elif choice == "6":
        clear_all_agents()
    elif choice == "7":
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
