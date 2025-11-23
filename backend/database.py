import mysql.connector
import os
import base64
from dotenv import load_dotenv

load_dotenv()

def get_db_password():
    enc = os.getenv("DB_PASSWORD_ENC")
    if enc:
        try:
            return base64.b64decode(enc).decode("utf-8")
        except Exception as e:
            print(f"[WARN] No se pudo decodificar DB_PASSWORD_ENC: {e}")
            return os.getenv("DB_PASSWORD", "")
    return os.getenv("DB_PASSWORD", "")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3307")),
    "user": os.getenv("DB_USER", "salas_app"),
    "password": get_db_password(),
    "database": os.getenv("DB_NAME", "ucu_salas"),
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)