import sqlite3
import logging
from typing import Dict, List, Optional
from objects import User, Message

logging.basicConfig(level=logging.INFO)

class DatabaseManagement:
    """
    Handles persistent storage of peers and messages using SQLite.
    Provides APIs for peer saving, message logging, and restoring state on startup.
    """

    def __init__(self, db_name: str = "peertalk.db"):
        """
        Initialize the database connection and cursor.
        
        :param db_name: Name of the SQLite database file.
        """
        try:
            self.conn = sqlite3.connect(db_name, check_same_thread=False)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def setup_database(self) -> None:
        """
        Creates the required database tables for peers and messages if they do not exist.
        """
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS peers (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    online INTEGER,
                    ip_address TEXT,
                    port INTEGER,
                    connection_key TEXT
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id TEXT,
                    receiver_id TEXT,
                    content TEXT
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database setup error: {e}")

    def save_peer(self, user: User) -> None:
        """
        Saves or updates a peer in the database.

        :param user: User object representing the peer.
        """
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO peers (user_id, name, online, ip_address, port, connection_key)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user.user_id, user.name, int(user.online), user.ip_address, user.port, user.connection_key))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Failed to save peer {user.user_id}: {e}")

    def get_all_peers(self) -> Dict[str, User]:
        """
        Loads all peers from the database and their associated messages.

        :return: Dictionary of user_id to User objects.
        """
        peers = {}
        try:
            self.cursor.execute("SELECT * FROM peers")
            rows = self.cursor.fetchall()
            for row in rows:
                user = User(
                    user_id=row[0],
                    name=row[1],
                    online=bool(row[2]),
                    ip_address=row[3],
                    port=row[4],
                    connection_key=row[5]
                )
                user.messages = self.get_messages(user.user_id)
                peers[user.user_id] = user
        except sqlite3.Error as e:
            logging.error(f"Failed to fetch peers: {e}")
        return peers

    def send_message(self, sender_id: str, receiver_id: str, content: str) -> None:
        """
        Persists a message between peers in the database.

        :param sender_id: Sender's user ID.
        :param receiver_id: Receiver's user ID.
        :param content: The message content.
        """
        try:
            self.cursor.execute('''
                INSERT INTO messages (sender_id, receiver_id, content)
                VALUES (?, ?, ?)
            ''', (sender_id, receiver_id, content))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Failed to save message from {sender_id} to {receiver_id}: {e}")

    def get_messages(self, user_id: str) -> List[Message]:
        """
        Retrieves all messages sent or received by a specific user.

        :param user_id: The user's ID.
        :return: List of Message objects.
        """
        messages = []
        try:
            self.cursor.execute('''
                SELECT sender_id, content FROM messages
                WHERE sender_id = ? OR receiver_id = ?
            ''', (user_id, user_id))
            rows = self.cursor.fetchall()
            messages = [Message(sender_id=row[0], content=row[1]) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Failed to retrieve messages for user {user_id}: {e}")
        return messages
