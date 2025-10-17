import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    # Try relative import first
    from ..connection import engine, Base
    from .. import models
except ImportError:
    # Fallback to absolute import
    from database.connection import engine, Base
    from database import models

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created.")