from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import uvicorn
import os
import json
import logging
from pathlib import Path
from typing import Optional
from functions import *
from helpers import (
    get_task_analysis,
    process_image,
    get_text_embeddings,
    find_similar_texts,
    make_request,
    validate_file_access,
    parse_task,
    analyze_task_constraints
)


from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="LLM-Based Automation Agent")

class TaskResponse(BaseModel):
    status: str
    message: Optional[str] = None
    error: Optional[str] = None

# Task mapping dictionary
TASK_MAP = {
    'do_a1': do_a1,
    'do_a2': do_a2,
    'do_a3': do_a3,
    'do_a4': do_a4,
    'do_a5': do_a5,
    'do_a6': do_a6,
    'do_a7': do_a7,
    'do_a8': do_a8,
    'do_a9': do_a9,
    'do_a10': do_a10
}

@app.post("/run")
async def run_task(task: str) -> TaskResponse:
    try:
        # Security check
        security_check = analyze_task_constraints(task)
        if isinstance(security_check, int):
            raise HTTPException(status_code=security_check, detail="Security analysis failed")
            
        # Handle case where security_check is not valid JSON
        try:
            security_result = json.loads(security_check)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid security check response")
            
        if not security_result.get('is_safe', False):
            raise HTTPException(
                status_code=400, 
                detail=f"Security violations detected: {security_result.get('violations', [])}"
            )

        # Parse task
        parsed_task = parse_task(task)
        if isinstance(parsed_task, int):
            raise HTTPException(status_code=parsed_task, detail="Task parsing failed")
            
        try:
            task_info = json.loads(parsed_task)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid task parsing response")
            
        func_name = task_info.get('func_name')
        if func_name not in TASK_MAP:
            raise HTTPException(status_code=400, detail="Invalid task function")

        # Execute task
        task_function = TASK_MAP[func_name]
        result = task_function(**task_info.get('arguments', {}))
            
        if isinstance(result, int):
            raise HTTPException(status_code=result, detail="Task execution failed")
            
        return TaskResponse(
            status="success",
            message="Task completed successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/read")
async def read_file(path: str):
    try:
        if not validate_file_access(path):
            raise HTTPException(
                status_code=400,
                detail="Invalid file path. Only files in /data directory are accessible"
            )
            
        file_path = Path(path)
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
            
        content = file_path.read_text()
        return Response(
            content=content,
            media_type="text/plain"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("File read failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)  # Fixed path (no leading "/")
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
