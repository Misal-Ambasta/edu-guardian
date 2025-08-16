#!/usr/bin/env python3
"""
Edu-Guardian Setup Script
-------------------------
This script initializes the Edu-Guardian backend environment.
"""

import os
import subprocess
import sys
from pathlib import Path

def create_venv():
    """Create a Python virtual environment"""
    print("Creating Python virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("Virtual environment created successfully.")

def install_requirements():
    """Install project requirements"""
    print("Installing required packages...")
    
    # Determine the Python executable path based on OS
    if os.name == 'nt':  # Windows
        pip_path = Path("venv") / "Scripts" / "pip"
    else:  # Unix-like systems
        pip_path = Path("venv") / "bin" / "pip"
    
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
    print("Required packages installed successfully.")

def setup_database():
    """Initialize the database schema"""
    print("Setting up database...")
    
    # Create a .env file if it doesn't exist
    if not os.path.exists(".env"):
        print("Creating default .env file...")
        with open(".env", "w") as f:
            f.write("""# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/edu_guardian_dev

# For production, use Neon DB URL:
# DATABASE_URL=postgres://user:password@ep-some-id.us-east-2.aws.neon.tech/edu_guardian

# Authentication
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ChromaDB Configuration
CHROMA_DB_PATH=./chromadb
""")
    
    # For simplicity in this setup script, we'll just print instructions
    print("""
Database setup instructions:
1. Make sure PostgreSQL is installed and running
2. Create a database named 'edu_guardian_dev'
3. Update the DATABASE_URL in .env if needed
4. Run migrations when ready with:
   - Activate your virtual environment
   - Run: python -m alembic upgrade head
""")

def setup_chromadb():
    """Initialize ChromaDB for vector embeddings"""
    print("Setting up ChromaDB...")
    
    # Create ChromaDB directory
    os.makedirs("chromadb", exist_ok=True)
    print("ChromaDB directory created.")
    
    print("""
ChromaDB setup instructions:
1. Make sure the CHROMA_DB_PATH in .env is set correctly
2. ChromaDB collections will be initialized on first run
""")

def main():
    """Main setup function"""
    print("Starting Edu-Guardian backend setup...")
    
    # Create virtual environment
    if not os.path.exists("venv"):
        create_venv()
    else:
        print("Virtual environment already exists, skipping creation.")
    
    # Install requirements
    install_requirements()
    
    # Setup database
    setup_database()
    
    # Setup ChromaDB
    setup_chromadb()
    
    print("""
Edu-Guardian backend setup completed!

To start the development server:
1. Activate your virtual environment:
   - Windows: .\\venv\\Scripts\\activate
   - Unix/MacOS: source venv/bin/activate
2. Run the server:
   - uvicorn app.main:app --reload

API documentation will be available at: http://localhost:8000/docs
""")

if __name__ == "__main__":
    main()
