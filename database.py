
import sqlite3

class DatabaseManagement:
    def __init__(self, db_name="peerchatdata.db"):
        """
        Initialize the database management system.

        Parameters:
            db_name (str): The name of the SQLite database file.
        """
        self.db_name = db_name
        self.setup_database()

    def setup_database(self):
        """
        Create 'users' and 'messages' tables in the database if they do not exist.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    online BOOLEAN NOT NULL,
                    ip_address TEXT,
                    port INTEGER,
                    connection_key TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id TEXT NOT NULL,
                    receiver_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(sender_id) REFERENCES users(id),
                    FOREIGN KEY(receiver_id) REFERENCES users(id)
                )
            ''')
            conn.commit()
        except sqlite3.Error as e:
            print("Database setup failed:", e)
        finally:
            conn.close()

    def _validate_user_data(self, user):
        """
        Validate that the required fields exist in the user dictionary and have correct types.

        Parameters:
            user (dict): Dictionary containing user information.

        Raises:
            ValueError: If required fields are missing or data types are incorrect.
        """
        required_fields = ['user_id', 'name', 'online', 'ip_address', 'port', 'connection_key']
        for field in required_fields:
            if field not in user:
                raise ValueError(f"Missing required field: {field}")

        if not isinstance(user['online'], bool):
            raise ValueError("Field 'online' must be a boolean")
        if not isinstance(user['port'], int):
            raise ValueError("Field 'port' must be an integer")

    def add_or_update_user(self, user):
        """
        Add a new user or update an existing user's information in the database.

        Parameters:
            user (dict): Dictionary with user information including id, name, status, IP, port, and connection key.
        """
        try:
            self._validate_user_data(user)
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (id, name, online, ip_address, port, connection_key)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user['user_id'], user['name'], user['online'], user['ip_address'], user['port'], user['connection_key']))
            conn.commit()
        except ValueError as ve:
            print("Validation Error:", ve)
        except sqlite3.IntegrityError:
            print("Integrity error: Possibly a duplicate user ID.")
        except sqlite3.Error as e:
            print("Error adding/updating user:", e)
        finally:
            conn.close()

    def get_all_users(self):
        """
        Retrieve all users from the database.

        Returns:
            list: A list of all user records.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()
            return users
        except sqlite3.Error as e:
            print("Error retrieving users:", e)
            return []
        finally:
            conn.close()

    def get_user_by_id(self, user_id):
        """
        Retrieve a user from the database using their unique ID.

        Parameters:
            user_id (str): The ID of the user to retrieve.

        Returns:
            tuple: The user record or None if not found.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print("Error retrieving user by ID:", e)
            return None
        finally:
            conn.close()

    def update_user_status(self, user_id, status):
        """
        Update a user's online status.

        Parameters:
            user_id (str): ID of the user.
            status (bool): New online status.
        """
        try:
            if not isinstance(status, bool):
                raise ValueError("Status must be a boolean")
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET online = ? WHERE id = ?', (status, user_id))
            conn.commit()
        except ValueError as ve:
            print("Validation Error:", ve)
        except sqlite3.Error as e:
            print("Error updating user status:", e)
        finally:
            conn.close()

    def send_message(self, sender_id, receiver_id, content):
        """
        Insert a message into the messages table.

        Parameters:
            sender_id (str): ID of the sender.
            receiver_id (str): ID of the receiver.
            content (str): Text content of the message.
        """
        try:
            if not all([sender_id, receiver_id, content]):
                raise ValueError("Sender, receiver, and content must not be empty")
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (sender_id, receiver_id, content) 
                VALUES (?, ?, ?)
            ''', (sender_id, receiver_id, content))
            conn.commit()
        except ValueError as ve:
            print("Validation Error:", ve)
        except sqlite3.IntegrityError:
            print("Integrity error: Sender or receiver ID might not exist.")
        except sqlite3.Error as e:
            print("Error sending message:", e)
        finally:
            conn.close()

    def get_messages_by_user(self, user_id):
        """
        Get all messages where the given user is either the sender or the receiver.

        Parameters:
            user_id (str): ID of the user.

        Returns:
            list: A list of message records.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM messages WHERE sender_id = ? OR receiver_id = ? ORDER BY timestamp ASC
            ''', (user_id, user_id))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print("Error retrieving messages for user:", e)
            return []
        finally:
            conn.close()

    def get_conversation(self, user1_id, user2_id):
        """
        Get all messages exchanged between two users.

        Parameters:
            user1_id (str): ID of the first user.
            user2_id (str): ID of the second user.

        Returns:
            list: A list of message records sorted by timestamp.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM messages 
                WHERE (sender_id = ? AND receiver_id = ?) 
                OR (sender_id = ? AND receiver_id = ?)
                ORDER BY timestamp ASC
            ''', (user1_id, user2_id, user2_id, user1_id))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print("Error retrieving conversation:", e)
            return []
        finally:
            conn.close()

    def delete_message(self, message_id):
        """
        Delete a message from the database using its ID.

        Parameters:
            message_id (int): ID of the message to delete.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))
            conn.commit()
        except sqlite3.Error as e:
            print("Error deleting message:", e)
        finally:
            conn.close()

    def get_online_users(self):
        """
        Retrieve all users who are currently online.

        Returns:
            list: A list of user records who are online.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE online = 1')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print("Error retrieving online users:", e)
            return []
        finally:
            conn.close()

    def clear_all_messages(self):
        """
        Delete all messages from the database.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages')
            conn.commit()
        except sqlite3.Error as e:
            print("Error clearing messages:", e)
        finally:
            conn.close()

    def clear_messages_by_user(self, user_id):
        """
        Delete all messages sent by a specific user.

        Parameters:
            user_id (str): ID of the user whose messages will be deleted.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages WHERE sender_id = ?', (user_id,))
            conn.commit()
        except sqlite3.Error as e:
            print("Error clearing messages by user:", e)
        finally:
            conn.close()
