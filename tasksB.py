# Phase B: LLM-based Automation Agent for DataWorks Solutions
from pathlib import Path
import os

DATA_ROOT = Path(os.getenv("DATA_ROOT", "/data"))
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

def B12(filepath):
    path = Path(filepath)
    return DATA_ROOT in path.parents or path == DATA_ROOT

# B3: Fetch Data from an API
def B3(url, save_path):
    full_path = DATA_ROOT / save_path
    if not B12(str(full_path)):
        return None
    import requests
    response = requests.get(url)
    with open(full_path, 'w') as file:
        file.write(response.text)

# B5: Run SQL Query
def B5(db_path, query, output_filename):
    full_db_path = DATA_ROOT / db_path
    full_output_path = DATA_ROOT / output_filename
    if not B12(str(full_db_path)) or not B12(str(full_output_path)):
        return None
    import sqlite3, duckdb
    conn = sqlite3.connect(full_db_path) if str(full_db_path).endswith('.db') else duckdb.connect(str(full_db_path))
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.close()
    with open(full_output_path, 'w') as file:
        file.write(str(result))
    return result

# B6: Web Scraping
def B6(url, output_filename):
    full_output_path = DATA_ROOT / output_filename
    import requests
    result = requests.get(url).text
    with open(full_output_path, 'w') as file:
        file.write(str(result))

# B7: Image Processing
def B7(image_path, output_path, resize=None):
    from PIL import Image
    full_image_path = DATA_ROOT / image_path
    full_output_path = DATA_ROOT / output_path
    if not B12(str(full_image_path)) or not B12(str(full_output_path)):
        return None
    img = Image.open(full_image_path)
    if resize:
        img = img.resize(resize)
    img.save(full_output_path)

# B9: Markdown to HTML Conversion
def B9(md_path, output_path):
    import markdown
    full_md_path = DATA_ROOT / md_path
    full_output_path = DATA_ROOT / output_path
    if not B12(str(full_md_path)) or not B12(str(full_output_path)):
        return None
    with open(full_md_path, 'r') as file:
        html = markdown.markdown(file.read())
    with open(full_output_path, 'w') as file:
        file.write(html)
