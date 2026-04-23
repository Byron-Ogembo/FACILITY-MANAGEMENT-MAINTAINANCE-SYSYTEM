import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db  # type: ignore
from app.app import create_app  # type: ignore

# Initialize database (creates tables from schema.sql)
init_db()

# Auto-seed demo data on Vercel and Render free tier (filesystem resets on cold start)
if os.environ.get('VERCEL') or os.environ.get('SEED_ON_START'):
    try:
        from seed_data import seed
        seed()
    except Exception as e:
        print(f"[wsgi] Seed skipped: {e}")

# Create application
app = create_app()
