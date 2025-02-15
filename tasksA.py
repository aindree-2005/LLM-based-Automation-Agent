import sqlite3
import subprocess
from dateutil.parser import parse
from datetime import datetime
import json
from pathlib import Path
import os
from fastapi import FastAPI, HTTPException, Query
import requests
from scipy.spatial.distance import cosine
from dotenv import load_dotenv

from pathlib import Path
load_dotenv()

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
DATA_ROOT = Path(os.getenv("DATA_ROOT", "/data"))

def A1(email="23f2000983@ds.study.iitm.ac.in"):
    try:
        process = subprocess.Popen(
            ["uv", "run", "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py", email],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error: {stderr}")
        return stdout
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error: {e.stderr}")
# A1()
def A2(prettier_version="prettier@3.4.2", filename="/data/format.md"):
    command = [r"C:\Program Files\nodejs\npx.cmd", prettier_version, "--write", filename]
    try:
        subprocess.run(command, check=True)
        print("Prettier executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def A3(filename='dates.txt', targetfile='dates-wednesdays.txt', weekday=2):
    input_file = DATA_ROOT / filename
    output_file = DATA_ROOT / targetfile
    weekday = weekday
    weekday_count = 0

    with open(input_file, 'r') as file:
        weekday_count = sum(1 for date in file if parse(date).weekday() == int(weekday)-1)

    with open(output_file, 'w') as file:
        file.write(str(weekday_count))
def A4(filename="contacts.json", targetfile="contacts-sorted.json"):
    # Load the contacts from the JSON file
    with open(DATA_ROOT / filename, 'r') as file:
        contacts = json.load(file)

    # Sort the contacts by last_name and then by first_name
    sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))

    # Write the sorted contacts to the new JSON file
    with open(DATA_ROOT / targetfile, 'w') as file:
        json.dump(sorted_contacts, file, indent=4)
def A5(log_dir_path='logs', output_file_path='logs-recent.txt', num_files=10):
    log_dir = DATA_ROOT / log_dir_path
    output_file = DATA_ROOT / output_file_path

    # Get list of .log files sorted by modification time (most recent first)
    log_files = sorted(log_dir.glob('*.log'), key=os.path.getmtime, reverse=True)[:num_files]

    # Read first line of each file and write to the output file
    with output_file.open('w') as f_out:
        for log_file in log_files:
            with log_file.open('r') as f_in:
                first_line = f_in.readline().strip()
                f_out.write(f"{first_line}\n")

def A6(doc_dir_path='docs', output_file_path='docs/index.json'):
    docs_dir = DATA_ROOT / doc_dir_path
    output_file = DATA_ROOT / output_file_path
    index_data = {}

    # Walk through all files in the docs directory
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = Path(root) / file
                # Read the file and find the first occurrence of an H1
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('# '):
                            # Extract the title text after '# '
                            title = line[2:].strip()
                            # Get the relative path without the prefix
                            relative_path = str(file_path.relative_to(docs_dir)).replace('\\', '/')
                            index_data[relative_path] = title
                            break  # Stop after the first H1

    # Write the index data to index.json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=4)
def A7(filename='email.txt', output_file='email-sender.txt'):
    # Read the content of the email
    with open(DATA_ROOT / filename, 'r') as file:
        email_content = file.readlines()

    sender_email = "ac@gmail.com"
    for line in email_content:
        if "From" == line[:4]:
            sender_email = (line.strip().split(" ")[-1]).replace("<", "").replace(">", "")
            break

    # Write the email address to the output file
    with open(DATA_ROOT / output_file, 'w') as file:
        file.write(sender_email)


import base64
def png_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_string
def A8(filename='credit_card.txt', image_path='credit_card.png'):
    # Construct the request body for the AIProxy call
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "There is 16 digit number is there in this image, with space after every 4 digit, only extract the those digit number without spaces and return just the number without any other characters. MAKE SURE THAT THERE IS EXACTLY 16 CHARACTERS-- NO MORE, AND CERTAINLY NO LESS"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{png_to_base64(DATA_ROOT / image_path)}"
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }

    # Make the request to the AIProxy service
    response = requests.post("http://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
                             headers=headers, data=json.dumps(body))

    # Extract the credit card number from the response
    result = response.json()
    card_number = result['choices'][0]['message']['content'].replace(" ", "")

    # Write the extracted card number to the output file
    with open(DATA_ROOT / filename, 'w') as file:
        file.write(card_number)
def get_embedding(text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    data = {
        "model": "text-embedding-3-small",
        "input": [text]
    }
    response = requests.post("http://aiproxy.sanand.workers.dev/openai/v1/embeddings", headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
def A9(filename=DATA_ROOT / 'comments.txt', output_filename=DATA_ROOT / 'comments-similar.txt'):
    # Load Sentence Transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Read comments
    with open(filename, 'r', encoding='utf-8') as f:
        comments = [line.strip() for line in f.readlines() if line.strip()]  # Remove empty lines

    # Ensure at least two comments exist
    if len(comments) < 2:
        print("Not enough comments to find similarities.")
        return

    # Compute embeddings
    embeddings = model.encode(comments, convert_to_numpy=True)

    # Compute cosine similarity matrix
    similarity_matrix = cosine_similarity(embeddings)

    # Ignore self-similarity by setting diagonal to -1
    np.fill_diagonal(similarity_matrix, -1)

    # Find the most similar pair
    max_index = np.unravel_index(np.argmax(similarity_matrix), similarity_matrix.shape)
    most_similar = (comments[max_index[0]], comments[max_index[1]])

    # Write the most similar pair to file
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(most_similar[0] + '\n')
        f.write(most_similar[1] + '\n')

    print(f"Most similar comments saved to {output_filename}")
def A10(filename='ticket-sales.db', output_filename='ticket-sales-gold.txt', query="SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"):
    # Connect to the SQLite database
    conn = sqlite3.connect(DATA_ROOT / filename)
    cursor = conn.cursor()

    # Calculate the total sales for the "Gold" ticket type
    cursor.execute(query)
    total_sales = cursor.fetchone()[0]

    # If there are no sales, set total_sales to 0
    total_sales = total_sales if total_sales else 0

    # Write the total sales to the file
    with open(DATA_ROOT / output_filename, 'w') as file:
        file.write(str(total_sales))

    # Close the database connection
    conn.close()
