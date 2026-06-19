import sqlite3
import json

DB_FILE = "dsa_sessions.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT PRIMARY KEY, 
                  user_name TEXT, 
                  api_key TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_state
                 (user_id TEXT PRIMARY KEY, 
                  algo_name TEXT, 
                  ai_data TEXT, 
                  qna_history TEXT)''')
    # NEW: Dedicated table for flashcard persistence
    c.execute('''CREATE TABLE IF NOT EXISTS user_flashcards
                 (user_id TEXT PRIMARY KEY, 
                  algo_name TEXT, 
                  cards_data TEXT, 
                  stats TEXT, 
                  card_idx INTEGER)''')
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
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO user_state (user_id, algo_name, ai_data, qna_history) VALUES (?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET algo_name=excluded.algo_name, ai_data=excluded.ai_data, qna_history=excluded.qna_history", 
              (user_id, algo_name, json.dumps(ai_data), json.dumps(qna_history)))
    conn.commit()
    conn.close()

def get_user_state(user_id):
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

# NEW: Flashcard state management functions
def save_flashcard_state(user_id, algo_name, cards_data, stats, card_idx):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO user_flashcards (user_id, algo_name, cards_data, stats, card_idx) VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET algo_name=excluded.algo_name, cards_data=excluded.cards_data, stats=excluded.stats, card_idx=excluded.card_idx",
              (user_id, algo_name, json.dumps(cards_data), json.dumps(stats), card_idx))
    conn.commit()
    conn.close()

def get_flashcard_state(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT algo_name, cards_data, stats, card_idx FROM user_flashcards WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "algo_name": row[0],
            "cards_data": json.loads(row[1]),
            "stats": json.loads(row[2]),
            "card_idx": row[3]
        }
    return None