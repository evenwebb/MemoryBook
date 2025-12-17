#!/usr/bin/env python3
"""
Development server runner
"""
import uvicorn
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Use .env.dev if it exists
    os.environ.setdefault("ENV_FILE", ".env.dev")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )

