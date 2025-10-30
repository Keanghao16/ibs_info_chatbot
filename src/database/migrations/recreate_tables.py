import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ..connection import engine, Base
from ..models import User, Admin, ChatSession, ChatMessage

def recreate_tables():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Tables recreated successfully!")

if __name__ == "__main__":
    recreate_tables()