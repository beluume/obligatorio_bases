import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'salas_app'),
    'password': os.getenv('DB_PASSWORD', 'SalasUCU2025!'),
    'database': os.getenv('DB_NAME', 'salas_estudio_ucu')
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)