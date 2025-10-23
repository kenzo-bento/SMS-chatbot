import sqlite3
import subprocess
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, SystemMessage
from datetime import datetime, timedelta
from langchain_core.prompts import PromptTemplate

def get_latest_phone_number():
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
    Retrieve the most recent SMS messages from a specified phone number.

    This function connects to the local macOS Messages database (`chat.db`),
    queries messages from the given `number`, and returns the last `limit` messages
    received from that number (excluding messages sent by the user).

    Args:
        number (str): The phone number or contact ID to fetch messages from.
        limit (int): The maximum number of recent messages to retrieve.

    Returns:
        str: A single string containing the messages in chronological order,
             separated by newline characters.

    Raises:
        sqlite3.OperationalError: If the Messages database cannot be accessed.
        FileNotFoundError: If the database file does not exist.

    Notes:
        - Only messages received (not sent by the user) are returned.
        - The function assumes the database is located at:
          `/Users/kennethsan/Library/Messages/chat.db`.

    Example:
        >>> get_messages_from_SMS("+1234567890", 5)
        "Hey, how's it going?\nAre you free tomorrow?\n..."
    """
    db_path = "/Users/kennethsan/Library/Messages/chat.db"
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
    Send an iMessage to a specified phone number using AppleScript on macOS.

    This function constructs and runs an AppleScript command to send the given
    `message` to the target phone number via the Messages app.

    Args:
        number (str): The phone number or contact ID to send the message to.
        message (str): The message content to send.

    Returns:
        None

    Raises:
        subprocess.CalledProcessError: If the AppleScript command fails.
        OSError: If the `osascript` executable cannot be found.

    Notes:
        - Works only on macOS with the Messages app configured.
        - Uses the iMessage service by default.
        - Ensure that Messages is running or accessible.

    Example:
        >>> send_imessage("+1234567890", "Hello there!")
        # Sends "Hello there!" to the specified number
    """
    script = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{number}" of targetService
        send "{message}" to targetBuddy
    end tell
    '''
    subprocess.run(["osascript", "-e", script])