"""
Drop and Recreate Chat Tables
Drops sessions and chat_messages tables and recreates them with fresh schema
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import text
from ..connection import engine, SessionLocal
from ..models import ChatSession, ChatMessage, User, Admin
from datetime import datetime

def drop_chat_tables():
    """Drop existing chat tables"""
    print("\n🗑️  Dropping existing chat tables...")
    
    try:
        with engine.connect() as connection:
            # Drop chat_messages first (has foreign key to sessions)
            print("  Dropping chat_messages table...")
            connection.execute(text("DROP TABLE IF EXISTS chat_messages"))
            connection.commit()
            print("  ✓ chat_messages table dropped")
            
            # Drop sessions table
            print("  Dropping sessions table...")
            connection.execute(text("DROP TABLE IF EXISTS sessions"))
            connection.commit()
            print("  ✓ sessions table dropped")
            
        print("✅ Tables dropped successfully\n")
        return True
        
    except Exception as e:
        print(f"❌ Error dropping tables: {str(e)}")
        return False


def create_chat_tables():
    """Create fresh chat tables"""
    print("📝 Creating fresh chat tables...")
    
    try:
        with engine.connect() as connection:
            # Create sessions table
            print("  Creating sessions table...")
            connection.execute(text("""
                CREATE TABLE sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id CHAR(36) NOT NULL,
                    admin_id CHAR(36) DEFAULT NULL,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_time DATETIME DEFAULT NULL,
                    status ENUM('waiting', 'active', 'closed') DEFAULT 'active',
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE SET NULL,
                    INDEX idx_user_id (user_id),
                    INDEX idx_admin_id (admin_id),
                    INDEX idx_status (status),
                    INDEX idx_id (id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            connection.commit()
            print("  ✓ sessions table created")
            
            # Create chat_messages table
            print("  Creating chat_messages table...")
            connection.execute(text("""
                CREATE TABLE chat_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT NOT NULL,
                    user_id CHAR(36) DEFAULT NULL,
                    admin_id CHAR(36) DEFAULT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_from_admin BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                    FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE SET NULL,
                    INDEX idx_session_id (session_id),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            connection.commit()
            print("  ✓ chat_messages table created")
            
        print("✅ Tables created successfully\n")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False


def verify_tables():
    """Verify that tables were created correctly"""
    print("🔍 Verifying table structure...")
    
    try:
        with engine.connect() as connection:
            # Check sessions table
            result = connection.execute(text("DESCRIBE sessions"))
            print("\n📋 sessions table structure:")
            for row in result:
                print(f"   {row[0]:20} {row[1]:20} {row[2]:5} {row[3]:5}")
            
            # Check chat_messages table
            result = connection.execute(text("DESCRIBE chat_messages"))
            print("\n📋 chat_messages table structure:")
            for row in result:
                print(f"   {row[0]:20} {row[1]:20} {row[2]:5} {row[3]:5}")
            
        print("\n✅ Table verification complete")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying tables: {str(e)}")
        return False


def main():
    """Main migration function"""
    print("\n" + "="*60)
    print("🔄 MIGRATION: Drop and Recreate Chat Tables")
    print("="*60)
    
    # Step 1: Drop tables
    if not drop_chat_tables():
        print("\n❌ Migration failed at drop step.")
        return
    
    # Step 2: Create tables
    if not create_chat_tables():
        print("\n❌ Migration failed at create step.")
        return
    
    # Step 3: Verify tables
    if not verify_tables():
        print("\n⚠️  Warning: Table verification failed.")
    
    print("\n" + "="*60)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY")
    print("="*60)
    print("\n📝 Summary:")
    print("   • sessions table recreated")
    print("   • chat_messages table recreated")
    print("   • All old data removed")
    print("   • Fresh schema applied with UUID foreign keys")
    print("\n")


if __name__ == '__main__':
    main()