from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import os
import sys
import asyncio
import logging
import requests

# AI Proxy Configuration
AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDA5ODNAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.LMIj06L44DC3uMCLjw6Of0aLyMlDEHKAGYLLZ86g8_8"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AIPROXY_TOKEN}"
}


BASE_URL_CHAT = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
BASE_URL_EMBEDDINGS = "http://aiproxy.sanand.workers.dev/openai/v1/embeddings"
BASE_URL_DEBUG = "http://localhost:11434/api/generate"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AIPROXY_TOKEN}"
}

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AIProxy")

def cosine_sim(embedding1, embedding2):
    return cosine_similarity([embedding1], [embedding2])[0][0]

def request_ai_proxy(payload, debug=False, embedding=False):
    """
    Sends a request to the AI Proxy API based on the payload and mode.

    Args:
        payload (dict): The JSON payload to send to the API.
        debug (bool): Whether to use the debug endpoint.
        embedding (bool): Whether to use the embeddings endpoint.

    Returns:
        dict or int: The response from the API or a status code in case of failure.
    """
    if embedding:
        logger.info("USING EMBEDDINGS")
        base_url = BASE_URL_EMBEDDINGS
    else:
        base_url = BASE_URL_CHAT

    if debug:
        base_url = BASE_URL_DEBUG

    try:
        response = requests.post(base_url, headers=HEADERS, json=payload)

        if response.status_code == 200:
            result = response.json()
            if debug:
                logger.info("USING DEBUG MODE")
                return result.get("choices", [{}])[0].get("message", "")

            if embedding:
                return result

            logger.info("USING OPENAI")
            return result["choices"][0]["message"]["content"]
        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.text)
            return response.status_code

    except Exception as e:
        logger.exception("An error occurred while making the API request.")
        return 500