from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import openai
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

# Basic setup

# Loading .env file (for API Key)
load_dotenv()

# OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Flask
app = Flask(__name__)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["3 per minute"]
)

# SQLite3
DATABASE = "./venv/sqlite/chat_logs.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                prompt TEXT,
                completion TEXT,
                timestamp DATETIME
            )
        ''')
        conn.commit()

init_db()

# Chat History (experimental)
def get_chat_history(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT prompt, completion FROM chat_logs
            WHERE user_id = ?
            ORDER BY timestamp ASC
        ''', (user_id,))
        return cursor.fetchall()

# Flask endpoints
@app.route('/openai-completion', methods=['POST'])
@limiter.limit("3 per minute")
def openai_completion():
    # Validate JSON
    data = request.get_json()
    if (not data) or ('prompt' not in data):
        return jsonify({"error": "Missing 'prompt' in request"}), 400

    # Extract prompt and user_id(?)
    prompt = data['prompt']
    user_id = data.get('user_id', 'anonymous')

    # Empty prompt error (only extra validation I can think of right now)
    if prompt.strip() == "":
        return jsonify({"error": "Empty 'prompt' provided"}), 400

    # Retreive history if any
    messages = []
    if user_id == 'anonymous':
        chat_history = []
    else:
        chat_history = get_chat_history(user_id)
        for h in chat_history:
            messages.append({"role": "user", "content": h[0]})  # Users prompt
            messages.append({"role": "assistant", "content": h[1]})  # ChatGPT response
    
    messages.append({"role": "user", "content": prompt}) #Newest message

    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo"
        )
        
        completion = response.choices[0].message.content

        # Log request and response to DB
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_logs (user_id, prompt, completion, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, prompt, completion, datetime.now()))
            conn.commit()

        # Return completion to the user
        return jsonify({"completion": completion}), 200

    except Exception as e:
        # Log error and return response
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)