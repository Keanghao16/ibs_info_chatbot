# src/database/migrations/add_photo_url_to_users.py
from sqlalchemy import text
from ..connection import engine

def run_migration():
    """Add photo_url column to users table"""
    with engine.connect() as conn:
        try:
            # Add column if it doesn't exist
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN photo_url VARCHAR(500) NULL
                AFTER is_premium
            """))
            conn.commit()
            print("✅ Successfully added photo_url column to users table")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("ℹ️  Column photo_url already exists")
            else:
                print(f"❌ Error: {e}")
                raise

if __name__ == '__main__':
    run_migration()