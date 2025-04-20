class ConnectionSuccess:
    def __init__(self, user):
        self.user = user

class ConnectionFailure:
    def __init__(self, reason):
        self.reason = reason

class Message:
    def __init__(self, sender_id, content):
        self.sender_id = sender_id
        self.content = content

class User:
    def __init__(self, user_id, name, online, ip_address, port, connection_key):
        self.user_id = user_id
        self.name = name
        self.online = online
        self.ip_address = ip_address
        self.port = port
        self.connection_key = connection_key
        self.messages = []

    def to_dict(self):
        return {
            'id': self.user_id,
            'name': self.name,
            'online': self.online,
            'ip_address': self.ip_address,
            'port': self.port,
            'connection_key': self.connection_key
        }