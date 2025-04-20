# logic.py
import time
import random
import threading
from models import *

class ChatService:
    def __init__(self, ui_callback):
        self.ui_callback = ui_callback
        self.discovery = None  # Not started by default
        self.users = {
            '1': User('1', 'Alice', True, '192.168.1.2', 5000, 'KEY123'),
            '2': User('2', 'Bob', False, '192.168.1.3', 5001, 'KEY456'),
            '3': User('3', 'Charlie', True, '192.168.1.4', 5002, 'KEY789'),
            '4': User('4', 'Diana', True, '192.168.1.5', 5003, 'KEY321'),
            '5': User('5', 'Eve', False, '192.168.1.6', 5004, 'KEY654'),
            '6': User('6', 'Frank', True, '192.168.1.7', 5005, 'KEY987'),
            '7': User('7', 'Grace', True, '192.168.1.8', 5006, 'KEY741'),
            '8': User('8', 'Heidi', False, '192.168.1.9', 5007, 'KEY852'),
            '9': User('9', 'Ivan', True, '192.168.1.10', 5008, 'KEY963'),
            '10': User('10', 'Judy', False, '192.168.1.11', 5009, 'KEY159'),
            '11': User('11', 'Mallory', True, '192.168.1.12', 5010, 'KEY258'),
            '12': User('12', 'Niaj', True, '192.168.1.13', 5011, 'KEY357'),
            '13': User('13', 'Olivia', False, '192.168.1.14', 5012, 'KEY456A'),
            '14': User('14', 'Peggy', True, '192.168.1.15', 5013, 'KEY654B'),
            '15': User('15', 'Sybil', False, '192.168.1.16', 5014, 'KEY789C'),
        }
    def start_discovery(self):
        from peer_discovery import PeerDiscovery  # Avoid circular import
        if self.discovery is None:
            self.discovery = PeerDiscovery(on_peer_found=self.add_peer)
            self.discovery.start()

    def stop_discovery(self):
        if self.discovery:
            self.discovery.running = False
            self.discovery = None

    def add_peer(self, ip):
        if ip not in self.users:
            peer_id = ip
            name = f"Peer {ip.split('.')[-1]}"
            user = User(user_id=peer_id, name=name, online=True, ip_address=ip, port=5000, connection_key="KEY")
            self.users[peer_id] = user
            self.ui_callback('peer_discovered')  # Tell GUI to refresh

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
