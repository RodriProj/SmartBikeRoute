import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

DB = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "smartbike_vilareal2"),
    "user": os.getenv("DB_USER", "smartbike"),
    "password": os.getenv("DB_PASSWORD", ""),
}
