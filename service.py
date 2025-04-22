import socket
import threading
import json
import uuid
import os
import time
from cryptography.fernet import Fernet
import logging
from objects import *
from database import DatabaseManagement

# --- Logging Setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("ChatService")
logger.setLevel(logging.NOTSET)


# --- Protocol ---
PROTOCOL = {
    'HELLO': 'HELLO',
    'KEY_EXCHANGE': 'KEY',
    'USER_INFO': 'USER',
    'MESSAGE': 'MSG',
    'ACK': 'ACK',
    'PING': 'PING',
    'PONG': 'PONG',
    'CONNECTION_REQUEST': 'CON_REQ',
    'CONNECTION_ACCEPT': 'CON_ACC',
    'CONNECTION_REJECT': 'CON_REJ',
}

# --- Files ----
os.makedirs("data", exist_ok=True)
KEY_FILE_PATH = "data/chat_key.key" 
CONFIG_FILE_PATH = "data/user_config.json"
DB_FILE_PATH = "data/chat_db.db"


def _load_or_generate_key():
        """Loads the Fernet key from a file or generates a new one if the file doesn't exist."""
        if os.path.exists(KEY_FILE_PATH):
            try:
                with open(KEY_FILE_PATH, "rb") as key_file:
                    key = key_file.read()
                    logger.info(f"Loaded Fernet key from {KEY_FILE_PATH}")
                    return key
            except Exception as e:
                logger.error(f"Error loading key from {KEY_FILE_PATH}: {e}")
                logger.info("Generating a new Fernet key.")
                return _generate_and_save_key()
        else:
            logger.info(f"{KEY_FILE_PATH} not found. Generating a new Fernet key.")
            return _generate_and_save_key()

def _generate_and_save_key():
    """Generates a new Fernet key and saves it to a file."""
    key = Fernet.generate_key()
    try:
        with open(KEY_FILE_PATH, "wb") as key_file:
            key_file.write(key)
        logger.info(f"Generated and saved Fernet key to {KEY_FILE_PATH}")
        return key
    except Exception as e:
        logger.error(f"Error saving key to {KEY_FILE_PATH}: {e}")
        return key


class ChatService:
    def __init__(self, ui_callback):
        self.ui_callback = ui_callback
        self.username, self.user_id = self.load_or_create_user_config()
        self.peers = {}
        self.active_port = None
        self.listener_thread = None
        self.key = _load_or_generate_key()
        self.cipher = Fernet(self.key)
        self.db_manager = DatabaseManagement(DB_FILE_PATH)
        self.db_manager.setup_database()

        saved_peers = self.db_manager.get_all_peers()
        for peer_id, user in saved_peers.items():
            self.peers[peer_id] = user.to_dict()
            self.peers[peer_id]['messages'] = user.messages


        logger.debug(f"Initialized ChatService with user_id={self.user_id}, username={self.username}")


    def run(self):
        self.active_port = self._find_open_port()
        logger.info(f"Service running on port {self.active_port}")
        self.listener_thread = threading.Thread(target=self._listen_for_connections, daemon=True)
        self.listener_thread.start()
        self._periodic_discovery()

    def load_or_create_user_config(self):
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "r") as file:
                config = json.load(file)
                if "username" in config and "user_id" in config:
                    return config["username"], config["user_id"]

        # Create new user credentials
        user_id = str(uuid.uuid4())
        username = f"user_{user_id[:8]}"

        config = {
            "username": username,
            "user_id": user_id
        }

        with open(CONFIG_FILE_PATH, "w") as file:
            json.dump(config, file, indent=4)

        return username, user_id


    def _find_open_port(self):
        for port in range(4400, 4406):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('0.0.0.0', port))
                s.listen()
                self.server_socket = s
                logger.debug(f"Bound to port {port}")
                return port
            except OSError:
                logger.debug(f"Port {port} in use, trying next...")
                continue
        logger.error("No available port in range 4400–4405")
        raise Exception("No available port in range 4400-4405")

    def _listen_for_connections(self):
        logger.info("Listening for incoming connections...")
        while True:
            client_socket, addr = self.server_socket.accept()
            logger.debug(f"Accepted connection from {addr}")
            threading.Thread(target=self._handle_connection, args=(client_socket,), daemon=True).start()

    def _handle_connection(self, sock):
        try:
            data = sock.recv(4096).decode()
            message = json.loads(data)
            logger.debug(f"Received message: {message}")
            if message['type'] == PROTOCOL['HELLO']:
                self._handle_hello(sock, message)
            elif message['type'] == PROTOCOL['MESSAGE']:
                self._handle_message(message)
            elif message['type'] == PROTOCOL['CONNECTION_REQUEST']:
                self._handle_connection_request(sock, message)
            elif message['type'] == PROTOCOL['CONNECTION_ACCEPT']:
                self._handle_connection_accept(sock, message)
            elif message['type'] == PROTOCOL['CONNECTION_REJECT']:
                self._handle_connection_reject(sock, message)
        except Exception as e:
            logger.exception(f"Connection error: {e}")
        finally:
            sock.close()

    def _handle_hello(self, sock, message):
        peer_id = message['user_id']
        peer_name = message['name']
        peer_port = message['port']
        peer_ip = sock.getpeername()[0]

        self.peers[peer_id] = {
            'id': peer_id,
            'name': peer_name,
            'online': True,
            'ip_address': peer_ip,
            'port': peer_port,
            'connection_key': None,
            'messages': self.get_existing_messages(peer_id)
        }

        peer_user = User(peer_id, peer_name, True, peer_ip, peer_port, None)
        self.db_manager.save_peer(peer_user)


        logger.info(f"Discovered peer: {peer_name} ({peer_id}) at {peer_ip}:{peer_port}")

        response = json.dumps({
            'type': PROTOCOL['USER_INFO'],
            'user_id': self.user_id,
            'name': self.username,
            'port': self.active_port
        }).encode()
        sock.send(response)
        logger.debug(f"Sent USER_INFO response to peer {peer_id}")

    def _handle_message(self, message):
        user_id = message['from']
        try:
            content = self.cipher.decrypt(message['data'].encode()).decode()
            logger.info(f"Received message from {user_id}: {content}")

            self.db_manager.send_message(sender_id=user_id, receiver_id=self.user_id, content=content)

            if user_id in self.peers:

                self.peers[user_id] = {
                    'id': user_id,
                    'name': f"User-{user_id[:5]}",
                    'ip_address': 'unknown',
                    'port': 0,
                    'messages': self.get_existing_messages(user_id),
                    'online': True
                }

            self.ui_callback({'type': 'new_message', 'from': user_id, 'content': content})

        except Exception as e:
            logger.error(f"Decryption failed: {e}")

    def get_existing_messages(self, peer_id):
        return self.db_manager.get_messages(peer_id)


    def _handle_connection_request(self, sock, message):
        peer_id = message['from']
        peer_name = message['name']
        peer_ip = sock.getpeername()[0]
        peer_port = message['port']


        self.peers[peer_id] = {
            'id': peer_id,
            'name': peer_name,
            'ip_address': peer_ip,
            'port': peer_port,
            'online': True,
            'messages': self.get_existing_messages(peer_id)
        }

        peer_user = User(peer_id, peer_name, True, peer_ip, peer_port, None)
        self.db_manager.save_peer(peer_user)

        self.ui_callback({'type': 'incoming_request', 'peer': self.peers[peer_id]})

    def _handle_connection_accept(self, sock, message):
        peer_id = message['from']
        self.ui_callback(ConnectionSuccess(self.peers[peer_id]))

    def _handle_connection_reject(self, sock, message):
        peer_id = message['from']
        self.ui_callback(ConnectionFailure(f"Connection request to {peer_id} was rejected."))



    def _periodic_discovery(self):
        while True:
            self._scan_ports()
            time.sleep(10)

    def _scan_ports(self):
        base_ip = "10.81.110.22"
        logger.debug("Starting peer discovery scan...")
        for port in range(4400, 4406):
            # if port == self.active_port:
            #     continue
            try:
                with socket.create_connection((base_ip, port), timeout=2) as sock:
                    hello = json.dumps({
                        'type': PROTOCOL['HELLO'],
                        'user_id': self.user_id,
                        'name': self.username,
                        'port': self.active_port
                    }).encode()
                    sock.send(hello)
                    logger.debug(f"Sent HELLO to {base_ip}:{port}")
            except Exception:
                logger.debug(f"No response from {base_ip}:{port}")

    def get_users(self):
        logger.debug("Fetching user list")
        return [peer for peer in self.peers.values()]

    def send_message(self, user_id, content):
        user = self.peers.get(user_id)
        if not user:
            logger.warning(f"Tried to send message to unknown user_id: {user_id}")
            return

        try:
            sock = socket.create_connection((user['ip_address'], user['port']), timeout=2)
            encrypted = self.cipher.encrypt(content.encode()).decode()
            msg = json.dumps({
                'type': PROTOCOL['MESSAGE'],
                'from': self.user_id,
                'data': encrypted
            }).encode()
            sock.send(msg)
            logger.info(f"Sent encrypted message to {user['name']} ({user_id})")

            self.db_manager.send_message(sender_id=self.user_id, receiver_id=user_id, content=content)

            self.peers[user_id].setdefault('messages', []).append(
                Message(sender_id=self.user_id, content=content)
            )

            self.ui_callback({'type': 'message_sent', 'to': user_id, 'content': content})

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
        finally:
            sock.close()


    def fetch_messages(self, user_id):
        user = self.peers.get(user_id)
        print(user)
        if user:
            return [{'from': msg.sender_id, 'message': msg.content} for msg in user['messages']]
        return []

    def get_discovered_peers(self):
        return list(self.peers.values())

    def connect_to_peer(self, user_id):
        user = self.peers.get(user_id)
        if not user:
            logger.warning(f"No user found with ID {user_id}")
            return

        try:
            with socket.create_connection((user['ip_address'], user['port']), timeout=2) as sock:
                req = json.dumps({
                    'type': PROTOCOL['CONNECTION_REQUEST'],
                    'from': self.user_id,
                    'name': self.username,
                    'port': self.active_port,
                }).encode()
                sock.send(req)
                logger.info(f"Sent CONNECTION_REQUEST to {user['name']}")

        except Exception as e:
            logger.error(f"Connection request failed: {e}")
            self.ui_callback(ConnectionFailure("Peer not reachable"))

    def respond_to_connection(self, peer_id: str, accept: bool):
        peer = self.peers.get(peer_id)
        if not peer:
            logger.warning(f"No peer found with ID {peer_id}")
            return

        response_type = PROTOCOL['CONNECTION_ACCEPT'] if accept else PROTOCOL['CONNECTION_REJECT']
        try:
            with socket.create_connection((peer['ip_address'], peer['port']), timeout=2) as sock:
                msg = json.dumps({
                    'type': response_type,
                    'from': self.user_id,
                }).encode()
                sock.send(msg)
            logger.info(f"Sent {response_type} to {peer['name']}")

            self.ui_callback({
            'type': 'connection_response_sent',
            'accepted': accept,
            'peer': peer
            })
        except Exception as e:
            logger.error(f"Failed to send connection response: {e}")


    def get_connection_code(self, user_id):
        return user_id[:6].upper()
