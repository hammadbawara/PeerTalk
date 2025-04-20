# peer_discovery.py
import socket
import threading
import time

BROADCAST_PORT = 50000
BROADCAST_INTERVAL = 3  # seconds
DISCOVERY_MESSAGE = b"PeerTalk::hello"

def get_own_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]
    except:
        return '127.0.0.1'
    finally:
        s.close()

class PeerDiscovery:
    def __init__(self, on_peer_found):
        self.running = True
        self.own_ip = get_own_ip()
        self.on_peer_found = on_peer_found

    def start(self):
        threading.Thread(target=self.broadcast_presence, daemon=True).start()
        threading.Thread(target=self.listen_for_peers, daemon=True).start()

    def broadcast_presence(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.running:
            sock.sendto(DISCOVERY_MESSAGE, ('<broadcast>', BROADCAST_PORT))
            time.sleep(BROADCAST_INTERVAL)

    def listen_for_peers(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', BROADCAST_PORT))
        while self.running:
            data, addr = sock.recvfrom(1024)
            ip = addr[0]
            if data == DISCOVERY_MESSAGE and ip != self.own_ip:
                self.on_peer_found(ip)
