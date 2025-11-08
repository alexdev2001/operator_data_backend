import pandas as pd
import os
from fastapi import UploadFile

UPLOAD_DIR = "app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


LAST_UPLOADED_FILE: str | None = None

async def save_uploaded_file(file: UploadFile):
    global LAST_UPLOADED_FILE
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    print(f"File path: {file_path}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    LAST_UPLOADED_FILE = file.filename
    save_latest_file_name(file.filename)
    return file_path


def parse_dataset(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        return f"File parsed: {len(df)} rows, {len(df.columns)} columns"
    except Exception as e:
        raise Exception(f"Error parsing file: {e}")

def save_latest_file_name(file_name: str):
    with open(os.path.join(UPLOAD_DIR, "latest.txt"), "w") as f:
        f.write(file_name)


def get_latest_file_name():
    path = os.path.join(UPLOAD_DIR, "latest.txt")
    if os.path.exists(path):
        with open(path) as f:
            return f.read().strip()
    return None