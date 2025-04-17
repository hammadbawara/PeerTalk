# ui.py
import threading
import customtkinter as ctk
from service import ChatService, ConnectionSuccess, ConnectionFailure

class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Local Network Chat")
        self.geometry("800x600")

        self.logic = ChatService(ui_callback=self.handle_logic_callback)
        threading.Thread(target=self.logic.run, daemon=True).start()

        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        self.btn_chat = ctk.CTkButton(self.sidebar, text="Chat", command=self.show_chat_list)
        self.btn_chat.pack(pady=10)

        self.btn_discover = ctk.CTkButton(self.sidebar, text="Discover", command=self.show_discover_page)
        self.btn_discover.pack(pady=10)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", expand=True, fill="both")

        self.chat_users_frame = None
        self.chat_page_frame = None
        self.discover_frame = None
        self.current_user = None

        self.show_chat_list()

    def show_chat_list(self):
        self.clear_main_frame()

        self.chat_users_frame = ctk.CTkFrame(self.main_frame)
        self.chat_users_frame.pack(expand=True, fill="both")

        users = self.logic.get_users()
        for user in users:
            ctk.CTkButton(
                self.chat_users_frame,
                text=f"{user['name']} ({'Online' if user['online'] else 'Offline'})",
                command=lambda u=user: self.open_chat(u)
            ).pack(pady=5)

    def open_chat(self, user):
        self.current_user = user
        self.clear_main_frame()

        self.chat_page_frame = ctk.CTkFrame(self.main_frame)
        self.chat_page_frame.pack(expand=True, fill="both")

        top_bar = ctk.CTkFrame(self.chat_page_frame)
        top_bar.pack(fill="x")

        ctk.CTkButton(top_bar, text="Back", command=self.show_chat_list).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(top_bar, text=user['name']).pack(side="left", padx=5)
        ctk.CTkLabel(
            top_bar,
            text="Online" if user['online'] else "Offline",
            text_color="green" if user['online'] else "red"
        ).pack(side="left")

        chat_container = ctk.CTkFrame(self.chat_page_frame)
        chat_container.pack(expand=True, fill="both")

        self.chat_history_frame = ctk.CTkScrollableFrame(chat_container)
        self.chat_history_frame.pack(expand=True, fill="both")

        self.load_chat(user['id'])

        bottom_bar = ctk.CTkFrame(self.chat_page_frame)
        bottom_bar.pack(fill="x", padx=5, pady=5)

        self.message_entry = ctk.CTkEntry(bottom_bar)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.message_entry.bind('<KeyRelease>', self.toggle_send_upload_buttons)

        self.send_button = ctk.CTkButton(bottom_bar, text="Send", command=self.send_message, state="disabled")
        self.send_button.pack(side="right", padx=5)

        self.upload_button = ctk.CTkButton(bottom_bar, text="Upload File", command=self.upload_file)
        self.upload_button.pack(side="right", padx=5)

    def load_chat(self, user_id):
        for widget in self.chat_history_frame.winfo_children():
            widget.destroy()

        messages = self.logic.fetch_messages(user_id)
        for msg in messages:
            side = "w" if msg['from'] == user_id else "e"
            label = ctk.CTkLabel(self.chat_history_frame, text=msg['message'], anchor=side, justify="left")
            label.pack(anchor=side, padx=10, pady=2)

    def toggle_send_upload_buttons(self, event=None):
        text = self.message_entry.get()
        if text.strip():
            self.send_button.configure(state="normal")
            self.upload_button.pack_forget()
        else:
            self.send_button.configure(state="disabled")
            self.upload_button.pack(side="right", padx=5)

    def send_message(self):
        message = self.message_entry.get()
        if message.strip():
            self.logic.send_message(self.current_user['id'], message)
            self.message_entry.delete(0, 'end')
            self.toggle_send_upload_buttons()
            self.load_chat(self.current_user['id'])

    def upload_file(self):
        print("Upload file clicked")

    def handle_logic_callback(self, result=None):
        if isinstance(result, ConnectionSuccess):
            self.open_chat(result.user)
        elif isinstance(result, ConnectionFailure):
            self.show_connection_failure(result.reason)

    def show_connection_failure(self, reason):
        self.clear_main_frame()
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(expand=True)
        ctk.CTkLabel(frame, text=f"Connection Failed: {reason}").pack(pady=10)
        ctk.CTkButton(frame, text="Back", command=self.show_discover_page).pack(pady=10)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_discover_page(self):
        self.clear_main_frame()
        self.discover_frame = ctk.CTkFrame(self.main_frame)
        self.discover_frame.pack(expand=True, fill="both")

        switch_frame = ctk.CTkFrame(self.discover_frame)
        switch_frame.pack(fill="x", pady=10)

        self.discovery_switch = ctk.CTkSwitch(switch_frame, text="Enable Discovery", command=self.toggle_discovery)
        self.discovery_switch.pack(side="left", padx=10)

        self.options_frame = ctk.CTkFrame(self.discover_frame)
        self.options_frame.pack(fill="x", padx=10, pady=5)
        self.options_frame.pack_forget()

        self.refresh_button = ctk.CTkButton(self.options_frame, text="Refresh", command=self.refresh_peers)
        self.refresh_button.pack(side="left", padx=5)

        self.manual_button = ctk.CTkButton(self.options_frame, text="Enter Manually", command=self.enter_peer_manually)
        self.manual_button.pack(side="left", padx=5)

        self.available_label = ctk.CTkLabel(self.discover_frame, text="Available Peers")
        self.available_list_frame = ctk.CTkFrame(self.discover_frame)

    def toggle_discovery(self):
        if self.discovery_switch.get():
            self.options_frame.pack(fill="x", padx=10, pady=5)
            self.available_label.pack(pady=(10, 0))
            self.available_list_frame.pack(fill="both", expand=True)
            self.refresh_peers()
        else:
            self.options_frame.pack_forget()
            self.available_label.pack_forget()
            self.available_list_frame.pack_forget()

    def refresh_peers(self):
        for widget in self.available_list_frame.winfo_children():
            widget.destroy()

        peers = self.logic.get_discovered_peers()
        for peer in peers:
            ctk.CTkButton(self.available_list_frame, text=peer['name'], command=lambda p=peer: self.show_connecting_ui(p)).pack(pady=5, padx=10, anchor="w")

    def enter_peer_manually(self):
        dialog = ctk.CTkInputDialog(text="Enter IP Address:", title="Manual Connection")
        ip = dialog.get_input()
        if ip:
            self.show_connecting_ui({'name': ip, 'id': ip})

    def show_connecting_ui(self, peer):
        self.clear_main_frame()
        request_frame = ctk.CTkFrame(self.main_frame)
        request_frame.pack(expand=True, fill="both", pady=20)

        self.connecting_label = ctk.CTkLabel(request_frame, text=f"Requesting {peer['name']} for connection...", font=("Arial", 16))
        self.connecting_label.pack(pady=10)

        self.code_label = ctk.CTkLabel(request_frame, text=f"Unique Code: {self.logic.get_connection_code(peer['id'])}", font=("Arial", 14))
        self.code_label.pack(pady=10)

        self.spinner = ctk.CTkLabel(request_frame, text="Connecting ⏳")
        self.spinner.pack(pady=10)

        ctk.CTkButton(request_frame, text="Cancel", command=self.show_discover_page).pack(pady=10)

        threading.Thread(target=self.logic.connect_to_peer, args=(peer['id'],), daemon=True).start()

if __name__ == '__main__':
    app = ChatApp()
    app.mainloop()
