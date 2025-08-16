#!/usr/bin/env python3
"""
Edu-Guardian Run Script
-----------------------
Simple script to run the Edu-Guardian API in development mode.
"""

import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Use environment variables if available
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"Starting Edu-Guardian API on http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
