import os
import sqlite3
from google import genai
from google.genai import types
import time 


# Global initialization of the unified Google GenAI Client
client = genai.Client()


def init_db():
    """Initializes the SQLite audit tracking database with a secure structural schema."""
    conn = sqlite3.connect('election_assistant_audit.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            content TEXT NOT NULL,
            temperature REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_audit_logs_count() -> int:
    """Utility function to count logged sessions for the UI frontend dashboard metrics."""
    try:
        conn = sqlite3.connect('election_assistant_audit.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM chat_history')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0

def generate_election_response(user_prompt: str, temperature_value: float) -> str:
    """
    Processes user prompts using the efficient gemini-2.5-flash model,
    implements defensive fallback validations, and saves records to an audit log.
    """
    init_db()

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=config
            )
            ai_response_text = response.text if (response and response.text) else "No response generated."
            break  # Success! Break out of the retry loop

        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                time.sleep(2)  # Wait 2 seconds before retrying
                continue
            else:
                ai_response_text = f"⚠️ Backend Engine Busy (503). Please try submitting again in a moment."
                break
    
    try:
        # Build the structured configuration object using specific SDK data types
        # Build the structured configuration object using specific SDK data types
        config = types.GenerateContentConfig(
            temperature=temperature_value,
            max_output_tokens=2500,
            system_instruction=(
                "You are DemocracyAI, an advanced, highly objective, non-partisan election audit assistant. "
                "Structure your answers beautifully using markdown tables, bullet points, and bold headers. "
                "CRITICAL: Always insert a blank newline (empty space line) directly before starting any markdown table or list structure. "
                "Example:\n\n| Item | Purpose |\n|---|---|\n| Sample | Data |\n\n"
                "Always maintain absolute technical neutrality and cite official procedural principles where relevant."
    )
)

        
        # Call generation endpoint using the standard lowercase, hyphenated string identifier
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=config
        )
        
        # Mandatory fallback valuation check to safely satisfy database NOT NULL constraints
        ai_response_text = response.text if (response and response.text) else "No response generated due to empty layout."
        
    except Exception as api_err:
        ai_response_text = f"⚠️ API Error encountered: {str(api_err)}"
    
    # Secure logging pipeline execution
    try:
        conn = sqlite3.connect('election_assistant_audit.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (prompt, content, temperature)
            VALUES (?, ?, ?)
        ''', (user_prompt, ai_response_text, temperature_value))
        conn.commit()
        conn.close()
    except Exception as db_err:
        print(f"Database Logging Failed: {db_err}")
        
    return ai_response_text