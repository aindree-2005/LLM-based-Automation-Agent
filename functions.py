import subprocess
from datetime import datetime
import json
import os
import sqlite3
from pathlib import Path
from .helpers import (
    get_text_embeddings, 
    process_image,
    make_request,
    find_similar_texts
)
def do_a1(email):
    subprocess.Popen([
        "uv", 
        "run",
        "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/datagen.py",
        email,
        "--root",
        "../data"
    ])
def do_a2():
    subprocess.run(["npx", "prettier@3.4.2", "--write", "/data/format.md"], check=True)

def do_a3():
    dates = Path("../data/dates.txt").read_text().splitlines()
    formats = ["%Y/%m/%d %H:%M:%S", "%Y-%m-%d", "%d-%b-%Y", "%b %d, %Y"]
    count = sum(any(datetime.strptime(d, f).weekday() == 2 for f in formats) for d in dates if d)
    Path("../data/dates-wednesdays.txt").write_text(str(count))

def do_a4():
    def contact_sort_key(contact):
        return (contact["last_name"], contact["first_name"])
    
    contacts = json.loads(Path("../data/contacts.json").read_text())
    sorted_contacts = sorted(contacts, key=contact_sort_key)
    Path("../data/contacts-sorted.json").write_text(json.dumps(sorted_contacts))
def do_a5():
    p = Path("../data/logs")
    latest = max(p.glob("*.log"), key=lambda x: int(x.stem.split("-")[1]))
    Path("../data/logs-recent.txt").write_text("".join(latest.read_text().splitlines(True)[:10]))

def do_a6():
    index = {}
    docs_dir = "../data/docs"
    
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                with open(os.path.join(root, file)) as f:
                    title = f.readline().strip("#").strip()
                    index[file] = title
    
    with open("../data/index.json", "w") as f:
        json.dump(index, f)
def do_a7():
    """Extract sender's email from email.txt"""
    # Read email content
    email_content = Path("../data/email.txt").read_text()
    
    messages = [
        {"role": "system", "content": "You are an email parser. Extract only the sender's email address from the email content. Return just the email address, nothing else."},
        {"role": "user", "content": email_content}
    ]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages
    }
    email_address = make_request(payload, 'chat')
    
    Path("../data/email-sender.txt").write_text(email_address.strip())

def do_a8():
    """Extract credit card number from image"""
    result = process_image("../data/credit-card.png")
    if isinstance(result, int):
        raise Exception(f"Image processing failed with status {result}")
        
    # Clean the number to contain only digits
    card_number = ''.join(c for c in result if c.isdigit())
    Path("../data/credit-card.txt").write_text(card_number)

def do_a9():
    """Find most similar pair of comments using embeddings"""
    comments = Path("../data/comments.txt").read_text().splitlines()
    similar_pair = find_similar_texts(comments)
    
    if isinstance(similar_pair, int):
        raise Exception(f"Finding similar texts failed with status {similar_pair}")
        
    idx1, idx2, _ = similar_pair
    similar_comments = f"{comments[idx1]}\n{comments[idx2]}"
    Path("../data/comments-similar.txt").write_text(similar_comments)
def do_a10():
    conn = sqlite3.connect("/data/ticket-sales.db")
    c= conn.cursor()
    c.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
    ts = c.fetchone()[0]
    conn.close()
    with open("/data/ticket-sales-gold.txt", "w") as f:
        f.write(str(ts))