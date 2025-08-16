"""
Script to run Alembic migrations automatically.
This script will:
1. Initialize Alembic if not already initialized
2. Run all available migrations
"""
import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migrations():
    print("Running database migrations...")
    
    # Check if alembic directory exists
    if not os.path.exists("alembic"):
        print("Alembic not initialized. Initializing now...")
        subprocess.run(["alembic", "init", "alembic"], check=True)
        print("Alembic initialized.")
    
    # Run migrations
    print("Applying all migrations...")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Migrations completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error applying migrations: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
