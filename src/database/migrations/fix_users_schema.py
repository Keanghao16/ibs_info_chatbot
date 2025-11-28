"""
Fix Users Table Schema
Adds missing columns: language_code, is_bot, is_premium, registration_date, last_activity
"""

from sqlalchemy import text
from ..connection import engine

def upgrade():
    """Add missing columns to users table"""
    with engine.connect() as conn:
        # Check if columns exist before adding
        result = conn.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'ibs_info_chatbot' 
            AND TABLE_NAME = 'users'
        """))
        
        existing_columns = [row[0] for row in result]
        
        # Add language_code
        if 'language_code' not in existing_columns:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN language_code VARCHAR(10) NULL AFTER last_name
            """))
            print("✅ Added language_code column")
        
        # Add is_bot
        if 'is_bot' not in existing_columns:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN is_bot BOOLEAN DEFAULT FALSE AFTER language_code
            """))
            print("✅ Added is_bot column")
        
        # Add is_premium
        if 'is_premium' not in existing_columns:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN is_premium BOOLEAN DEFAULT FALSE AFTER is_bot
            """))
            print("✅ Added is_premium column")
        
        # Add registration_date
        if 'registration_date' not in existing_columns:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN registration_date DATETIME DEFAULT CURRENT_TIMESTAMP AFTER is_premium
            """))
            print("✅ Added registration_date column")
        
        # Add last_activity
        if 'last_activity' not in existing_columns:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN last_activity DATETIME NULL AFTER registration_date
            """))
            print("✅ Added last_activity column")
        
        conn.commit()
        print("\n🎉 Users table schema updated successfully!")

def downgrade():
    """Remove added columns"""
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users DROP COLUMN last_activity"))
        conn.execute(text("ALTER TABLE users DROP COLUMN registration_date"))
        conn.execute(text("ALTER TABLE users DROP COLUMN is_premium"))
        conn.execute(text("ALTER TABLE users DROP COLUMN is_bot"))
        conn.execute(text("ALTER TABLE users DROP COLUMN language_code"))
        conn.commit()
        print("✅ Downgrade complete")

if __name__ == '__main__':
    print("Running users table schema migration...")
    upgrade()