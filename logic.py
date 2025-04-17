# logic.py
import time
import threading

class ChatLogic:
    def __init__(self, ui_callback):
        self.ui_callback = ui_callback
        self._dummy_users = [
            {"id": 1, "name": "Alice", "online": True},
            {"id": 2, "name": "Bob", "online": False},
            {"id": 3, "name": "Charlie", "online": True}
        ]
        self._messages = {
            1: [
                {"from": 1, "message": "Hi there!"},
                {"from": 0, "message": "Hello Alice!"}
            ],
            2: [
                {"from": 2, "message": "Hey!"},
                {"from": 0, "message": "Hi Bob."}
            ],
            3: []
        }
        self._running = True

    def run(self):
        # Dummy background task to simulate incoming messages
        while self._running:
            time.sleep(10)
            # Randomly simulate a new message from Alice
            self._messages[1].append({"from": 1, "message": "Another ping!"})
            self.ui_callback()

    def get_users(self):
        return self._dummy_users

    def fetch_messages(self, user_id):
        return self._messages.get(user_id, [])

    def send_message(self, user_id, message):
        # Simulate sending a message
        if user_id in self._messages:
            self._messages[user_id].append({"from": 0, "message": message})
        else:
            self._messages[user_id] = [{"from": 0, "message": message}]
        self.ui_callback()

    def stop(self):
        self._running = False