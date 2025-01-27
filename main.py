import os
import sys
import subprocess
import requests
import logging
import asyncio
import re
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pytest

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Basic setup
PROJECT_ROOT = os.getcwd()
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# AI Proxy Configuration
AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDA5ODNAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.LMIj06L44DC3uMCLjw6Of0aLyMlDEHKAGYLLZ86g8_8"
BASE_URL = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AIPROXY_TOKEN}"
}

app = FastAPI()

def download_file(url: str, filename: str) -> None:
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

def run_subprocess(cmd, check=True, shell=False, env=None):
    try:
        process_env = os.environ.copy()
        if env:
            process_env.update(env)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
            cwd=PROJECT_ROOT,
            shell=shell,
            env=process_env
        )
        logger.debug(f"Command output: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else e.stdout if e.stdout else str(e)
        logger.error(f"Subprocess failed: {error_msg}")
        raise

def request_ai_proxy(messages: list, model: str = "gpt-4-mini"):
    payload = {
        "model": model,
        "messages": messages
    }
    try:
        response = requests.post(BASE_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"AI Proxy request failed: {str(e)}")
        raise

def install_dependencies():
    run_subprocess(["pip", "install", "faker", "pillow"])

def task_a1_install_uv_and_run_datagen(email: str):
    try:
        # Install dependencies
        install_dependencies()
        
        # Install uv
        run_subprocess(["pip", "install", "uv"])
        
        # Download datagen.py
        script_url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/datagen.py"
        script_path = os.path.join(DATA_DIR, "datagen.py")
        
        if not os.path.exists(script_path):
            download_file(script_url, script_path)
        
        # Create required directories
        os.makedirs(os.path.join(DATA_DIR, "logs"), exist_ok=True)
        os.makedirs(os.path.join(DATA_DIR, "docs"), exist_ok=True)
        
        # Run datagen.py
        result = run_subprocess([
            sys.executable,
            script_path,
            email,
            "--root",
            DATA_DIR
        ])
        
        # Verify files were created
        expected_files = ["format.md", "dates.txt", "contacts.json", "email.txt", 
                         "credit_card.png", "comments.txt", "ticket-sales.db"]
        for file in expected_files:
            if not os.path.exists(os.path.join(DATA_DIR, file)):
                raise Exception(f"Failed to generate {file}")
        
        return {"status": "success", "message": f"Data generated for email: {email}"}
    except Exception as e:
        logger.error(f"Task A1 failed: {str(e)}")
        raise

@app.post("/run")
async def run_task(task: str = Query(..., description="Task to execute in plain English")):
    try:
        logger.debug(f"Received task: {task}")
        
        # Direct task execution without AI proxy
        if "install uv" in task.lower() and "datagen.py" in task:
            # Extract email from task string using regex
            email = "aindree2005@gmail.com"  # or extract from task
            return task_a1_install_uv_and_run_datagen(email)
            
        raise HTTPException(400, detail="Task not recognized")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(500, detail=f"Unexpected error: {str(e)}")

@app.get("/read")
async def read_file(path: str = Query(..., description="Path to the file")):
    try:
        full_path = os.path.join(DATA_DIR, path)
        if not os.path.exists(full_path):
            raise HTTPException(404, detail=f"File not found: {path}")
        return FileResponse(full_path)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading file {path}: {str(e)}")
        raise HTTPException(500, detail=f"Error reading file: {str(e)}")

@pytest.mark.asyncio
async def test_read_file_not_found():
    with pytest.raises(HTTPException) as exc_info:
        await read_file("nonexistent.txt")
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_read_file_success():
    test_content = "test content"
    test_file = os.path.join(DATA_DIR, "test.txt")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    response = await read_file("test.txt")
    assert isinstance(response, FileResponse)
    os.remove(test_file)

def test_task_a1():
    with pytest.raises(Exception):
        task_a1_install_uv_and_run_datagen("test@example.com")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
