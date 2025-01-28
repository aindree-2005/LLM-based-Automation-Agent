import subprocess
from datetime import datetime
import json
import os
import sqlite3

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
    subprocess.Popen([
        "prettier",
        "../data/format.md",
        "--write",
        "--parser",
        "markdown"
    ])
