import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db  # type: ignore
from app.app import create_app  # type: ignore

# Initialize database
init_db()

# Create application
app = create_app()
