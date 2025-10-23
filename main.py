import sqlite3
import time
import threading
import os
from helper import *
from rag import get_response

DB_PATH = "/Users/username/Library/Messages/chat.db"

last_id = 0

def get_latest_message_info():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.rowid, h.id
            FROM message m
            JOIN handle h ON m.handle_id = h.rowid
            ORDER BY m.date DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()
        if result:
            return result  # (rowid, sender)
        return (0, None)
    except Exception as e:
        print("Error reading database:", e)
        return (0, None)

def delayed_run():
    time.sleep(10) # checking for extra messages
    number = get_latest_phone_number()
    message = get_messages_from_SMS(number, 5)
    response = get_response(message)
    send_imessage(number, response)

while True:
    new_id, sender = get_latest_message_info()
    if new_id > last_id+1:
        delayed_run()
        last_id = new_id
    time.sleep(10)

