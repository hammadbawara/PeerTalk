# logic.py
import time
import random
import threading
from objects import *

class ChatService:
    def __init__(self, ui_callback):
        self.ui_callback = ui_callback
        self.users = {
            '1': User('1', 'Alice', True, '192.168.1.2', 5000, 'KEY123'),
            '2': User('2', 'Bob', False, '192.168.1.3', 5001, 'KEY456'),
        }

    def run(self):
        # Placeholder thread runner
        while True:
            time.sleep(1)

    def get_users(self):
        return [user.to_dict() for user in self.users.values()]

    def fetch_messages(self, user_id):
        return [{'from': msg.sender_id, 'message': msg.content} for msg in self.users[user_id].messages]

    def send_message(self, user_id, message):
        msg = Message(sender_id='me', content=message)
        self.users[user_id].messages.append(msg)
        self.users[user_id].messages.append(Message(sender_id=user_id, content=f"Echo: {message}"))

    def get_discovered_peers(self):
        return [user.to_dict() for user in self.users.values() if user.online]

    def get_connection_code(self, peer_id):
        return self.users[peer_id].connection_key

    def connect_to_peer(self, peer_id):
        time.sleep(2)
        if random.choice([True, False]):
            self.ui_callback(ConnectionSuccess(self.users[peer_id].to_dict()))
        else:
            self.ui_callback(ConnectionFailure("Peer not responding"))
