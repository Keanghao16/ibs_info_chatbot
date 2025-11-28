"""
Recreate Sessions and Messages Tables with Proper Schema
Drops existing tables and creates new ones with session_id in messages
"""

from sqlalchemy import text
from ..connection import engine, SessionLocal
from ..models import User, Admin
import traceback

def backup_existing_data(db):
    """Backup existing session and message data"""
    try:
        # Try to backup existing data
        sessions_backup = db.execute(text("""
            SELECT id, user_id, admin_id, start_time, end_time, status 
            FROM sessions
        """)).fetchall()
        
        messages_backup = db.execute(text("""
            SELECT id, user_id, admin_id, message, timestamp, is_from_admin 
            FROM chat_messages
        """)).fetchall()
        
        print(f"📦 Backed up {len(sessions_backup)} sessions and {len(messages_backup)} messages")
        return sessions_backup, messages_backup
    except Exception as e:
        print(f"⚠️  No existing data to backup: {e}")
        return [], []


def drop_existing_tables(db):
    """Drop existing sessions and chat_messages tables"""
    print("\n🗑️  Dropping existing tables...")
    
    try:
        # Drop in correct order (child tables first)
        db.execute(text("DROP TABLE IF EXISTS chat_messages"))
        print("  ✅ Dropped chat_messages table")
        
        db.execute(text("DROP TABLE IF EXISTS sessions"))
        print("  ✅ Dropped sessions table")
        
        db.commit()
        print("✅ Old tables dropped successfully\n")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        db.rollback()
        raise


def create_new_tables(db):
    """Create new sessions and chat_messages tables with proper schema"""
    print("🔨 Creating new tables with proper schema...")
    
    try:
        # Create sessions table
        db.execute(text("""
            CREATE TABLE sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id CHAR(36) NOT NULL,
                admin_id CHAR(36) NULL,
                start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME NULL,
                status ENUM('waiting', 'active', 'closed') NOT NULL DEFAULT 'waiting',
                
                -- Foreign keys
                CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT fk_sessions_admin FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE SET NULL,
                
                -- Indexes
                INDEX idx_sessions_user (user_id),
                INDEX idx_sessions_admin (admin_id),
                INDEX idx_sessions_status (status),
                INDEX idx_sessions_start_time (start_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("  ✅ Created sessions table")
        
        # Create chat_messages table
        db.execute(text("""
            CREATE TABLE chat_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT NOT NULL,
                user_id CHAR(36) NOT NULL,
                admin_id CHAR(36) NULL,
                message TEXT NOT NULL,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_from_admin BOOLEAN NOT NULL DEFAULT FALSE,
                
                -- Foreign keys
                CONSTRAINT fk_messages_session FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                CONSTRAINT fk_messages_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT fk_messages_admin FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE SET NULL,
                
                -- Indexes
                INDEX idx_messages_session (session_id),
                INDEX idx_messages_user (user_id),
                INDEX idx_messages_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("  ✅ Created chat_messages table")
        
        db.commit()
        print("✅ New tables created successfully\n")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        traceback.print_exc()
        db.rollback()
        raise


def verify_tables(db):
    """Verify new tables structure"""
    print("🔍 Verifying new table structures...")
    
    try:
        # Check sessions table
        result = db.execute(text("DESCRIBE sessions"))
        sessions_columns = [row[0] for row in result]
        print(f"  ✅ sessions table columns: {', '.join(sessions_columns)}")
        
        # Check chat_messages table
        result = db.execute(text("DESCRIBE chat_messages"))
        messages_columns = [row[0] for row in result]
        print(f"  ✅ chat_messages table columns: {', '.join(messages_columns)}")
        
        # Verify session_id exists in chat_messages
        if 'session_id' in messages_columns:
            print("  ✅ session_id foreign key properly added to chat_messages")
        else:
            print("  ❌ session_id NOT found in chat_messages!")
            
        print("\n✅ Table verification complete\n")
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        traceback.print_exc()


def create_test_data(db):
    """Create test chat sessions with messages"""
    print("🌱 Creating test data...")
    
    try:
        # Get a test user and admin
        user = db.query(User).first()
        admin = db.query(Admin).first()
        
        if not user:
            print("⚠️  No users found. Please run seed_users.py first.")
            return
        
        if not admin:
            print("⚠️  No admins found. Skipping admin assignment.")
        
        # Create 3 test sessions
        sessions_created = 0
        
        for i in range(3):
            # Insert session
            result = db.execute(text("""
                INSERT INTO sessions (user_id, admin_id, status, start_time)
                VALUES (:user_id, :admin_id, :status, NOW() - INTERVAL :hours HOUR)
            """), {
                'user_id': user.id,
                'admin_id': admin.id if admin else None,
                'status': ['waiting', 'active', 'closed'][i],
                'hours': i + 1
            })
            
            session_id = result.lastrowid
            sessions_created += 1
            
            # Add test messages to session
            for j in range(3):
                db.execute(text("""
                    INSERT INTO chat_messages (session_id, user_id, admin_id, message, is_from_admin, timestamp)
                    VALUES (:session_id, :user_id, :admin_id, :message, :is_from_admin, NOW() - INTERVAL :minutes MINUTE)
                """), {
                    'session_id': session_id,
                    'user_id': user.id,
                    'admin_id': admin.id if admin and j % 2 == 0 else None,
                    'message': f'Test message {j+1} in session {session_id}',
                    'is_from_admin': j % 2 == 0,
                    'minutes': (i * 60) + (j * 10)
                })
        
        db.commit()
        print(f"  ✅ Created {sessions_created} test sessions with messages")
        print("✅ Test data creation complete\n")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        traceback.print_exc()
        db.rollback()


def main():
    """Main migration function"""
    print("\n" + "="*60)
    print("🔄 RECREATING SESSIONS AND MESSAGES TABLES")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        # Step 1: Backup existing data (optional)
        sessions_backup, messages_backup = backup_existing_data(db)
        
        # Step 2: Drop existing tables
        drop_existing_tables(db)
        
        # Step 3: Create new tables with proper schema
        create_new_tables(db)
        
        # Step 4: Verify new structure
        verify_tables(db)
        
        # Step 5: Create test data
        create_test_data(db)
        
        print("="*60)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📝 Summary:")
        print(f"  • Dropped old tables")
        print(f"  • Created new sessions table (id: INT, user_id/admin_id: UUID)")
        print(f"  • Created new chat_messages table (id: INT, session_id: INT FK)")
        print(f"  • Added proper foreign keys and indexes")
        print(f"  • Created {3} test sessions")
        print("\n✅ You can now test the API endpoints!")
        print("="*60 + "\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ MIGRATION FAILED")
        print("="*60)
        print(f"\nError: {str(e)}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    # Ask for confirmation
    print("\n⚠️  WARNING: This will DROP existing sessions and chat_messages tables!")
    print("   All chat history will be lost.")
    response = input("\nDo you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        main()
    else:
        print("\n❌ Migration cancelled.")