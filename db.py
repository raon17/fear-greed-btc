import os
from dotenv import load_dotenv 
 
load_dotenv() 
 
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME", "btc_dashboard"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}
 
def get_db_url():
    c = DB_CONFIG
    return f"postgresql+psycopg2://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['dbname']}"
 