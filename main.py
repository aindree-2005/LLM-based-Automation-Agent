from fastapi import *
from functions import *
import uvicorn
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import os
import sys
import subprocess
import requests
import logging
import asyncio
from dotenv import load_dotenv
load_dotenv()

def cosine_sim(embedding1, embedding2):
    return cosine_similarity([embedding1], [embedding2])[0][0]

AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDA5ODNAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.LMIj06L44DC3uMCLjw6Of0aLyMlDEHKAGYLLZ86g8_8"
BASE_URL = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AIPROXY_TOKEN}"
}

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Basic setup
PROJECT_ROOT = os.getcwd()
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
