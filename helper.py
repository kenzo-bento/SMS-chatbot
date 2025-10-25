import sqlite3
import subprocess
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, SystemMessage
from datetime import datetime, timedelta
from langchain_core.prompts import PromptTemplate

def get_latest_phone_number():
    """
    this function retrieves the phone number of the latest text received
    """
    conn = sqlite3.connect("/Users/username/Library/Messages/chat.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT h.id
        FROM message m
        JOIN handle h ON m.handle_id = h.rowid
        ORDER BY m.rowid DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    return None

def get_messages_from_SMS(number:str, limit:int)-> str:
    """
    this function retrieves the most recent SMS messages from a specified phone number
    """
    db_path = "/Users/username/Library/Messages/chat.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT text, is_from_me, datetime(date/1000000000 + strftime('%s','2001-01-01'), 'unixepoch')
    FROM message m
    JOIN handle h ON m.handle_id = h.rowid
    WHERE h.id = ?        
    ORDER BY m.date DESC
    LIMIT ?;
    """, (number,limit))

    textlist = []
    for text, is_from_me, timestamp in cursor.fetchall():
        if not is_from_me and text:
            textlist.insert(0, text)

    return "\n".join(textlist)

def send_imessage(number:str, message:str)->None:
    """
    this function sends an iMessage to a specified phone number using AppleScript on macOS.
    """
    message = message.replace('"', '\\"') # to check for AppleScript syntax
    script = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{number}" of targetService
        send "{message}" to targetBuddy
    end tell
    '''
    subprocess.run(["osascript", "-e", script])
