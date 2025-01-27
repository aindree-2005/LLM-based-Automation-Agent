import re
import os
import sys
import subprocess
import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up data directory using current working directory
DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Verify AIPROXY_TOKEN
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    raise EnvironmentError("AIPROXY_TOKEN environment variable is not set.")

def extract_email(task: str) -> str:
    """Extract email from task description."""
    match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", task)
    return match.group(0) if match else None

def download_file(url: str, filename: str) -> None:
    """Download file from URL to specified path."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(response.content)
        logger.debug(f"File downloaded successfully to {filename}")
    except Exception as e:
        logger.error(f"Failed to download file from {url}: {str(e)}")
        raise

@app.post("/run")
async def run_task(task: str = Query(..., description="Task to execute in plain English")):
    """Execute the specified task."""
    try:
        logger.debug(f"Received task: {task}")
        
        # Task A1: Install uv and run datagen.py
        if "install uv" in task.lower() and "datagen.py" in task:
            email = extract_email(task)
            if not email:
                raise HTTPException(400, detail="Email not specified in the task.")
            
            # Install uv
            logger.debug("Installing uv")
            try:
                subprocess.run(["pip", "install", "uv"], 
                             capture_output=True, 
                             text=True, 
                             check=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install uv: {e.stdout} {e.stderr}")
                raise HTTPException(500, detail="Failed to install uv")
            
            # Download and run datagen.py
            script_url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/datagen.py"
            script_path = os.path.join(DATA_DIR, "datagen.py")
            
            try:
                download_file(script_url, script_path)
                logger.debug(f"Running script with email: {email}")
                result = subprocess.run([sys.executable, script_path, email], 
                                     capture_output=True, 
                                     text=True, 
                                     check=True)
                logger.debug(f"Script output: {result.stdout}")
                return {"status": "success", "message": f"Data generated for email: {email}"}
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr if e.stderr else e.stdout if e.stdout else str(e)
                logger.error(f"Script execution failed: {error_msg}")
                raise HTTPException(500, detail=f"Script execution failed: {error_msg}")
        
        # Task A2: Format markdown file using prettier
        elif "prettier" in task.lower() and "/data/format.md" in task:
            try:
                subprocess.run(["prettier", "--write", os.path.join(DATA_DIR, "format.md")],
                             capture_output=True,
                             text=True,
                             check=True)
                return {"status": "success", "message": "File formatted successfully"}
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr if e.stderr else str(e)
                raise HTTPException(500, detail=f"Prettier formatting failed: {error_msg}")
        
        # Add handlers for tasks A3-A10 and B1-B10 here
        
        raise HTTPException(400, detail="Task not recognized")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(500, detail=f"Unexpected error: {str(e)}")

@app.get("/read")
async def read_file(path: str = Query(..., description="Path to the file")):
    """Read and return the contents of a file."""
    try:
        full_path = os.path.join(DATA_DIR, path)
        if not os.path.exists(full_path):
            raise HTTPException(404, detail="File not found")
        return FileResponse(full_path)
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        raise HTTPException(500, detail=f"Error reading file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
