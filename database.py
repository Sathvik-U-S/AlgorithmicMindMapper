import sqlite3
import json

DB_FILE = "dsa_sessions.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Stores user credentials
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT PRIMARY KEY, 
                  user_name TEXT, 
                  api_key TEXT)''')
    # Stores the user's active workspace state
    c.execute('''CREATE TABLE IF NOT EXISTS user_state
                 (user_id TEXT PRIMARY KEY, 
                  algo_name TEXT, 
                  ai_data TEXT, 
                  qna_history TEXT)''')
    conn.commit()
    conn.close()

def save_user_data(user_id, name, api_key):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, user_name, api_key) VALUES (?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET user_name=excluded.user_name, api_key=excluded.api_key", 
              (user_id, name, api_key))
    conn.commit()
    conn.close()

def get_user_data(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_name, api_key FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"user_name": row[0], "api_key": row[1]}
    return None

def save_user_state(user_id, algo_name, ai_data, qna_history):
    """Automatically saves the user's analysis and chat history so it loads on their next visit."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO user_state (user_id, algo_name, ai_data, qna_history) VALUES (?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET algo_name=excluded.algo_name, ai_data=excluded.ai_data, qna_history=excluded.qna_history", 
              (user_id, algo_name, json.dumps(ai_data), json.dumps(qna_history)))
    conn.commit()
    conn.close()

def get_user_state(user_id):
    """Retrieves the last active session for a specific user ID."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT algo_name, ai_data, qna_history FROM user_state WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "algo_name": row[0],
            "ai_data": json.loads(row[1]),
            "qna_history": json.loads(row[2])
        }
    return None