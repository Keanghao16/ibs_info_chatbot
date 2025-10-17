from src.database.connection import engine, Base
from src.database.models import User, Admin, ChatSession, ChatMessage

def recreate_tables():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Tables recreated successfully!")

if __name__ == "__main__":
    recreate_tables()