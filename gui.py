# ui.py
import threading
import customtkinter as ctk
from logic import ChatLogic

class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Local Network Chat")
        self.geometry("800x600")

        self.logic = ChatLogic(ui_callback=self.update_ui)
        threading.Thread(target=self.logic.run, daemon=True).start()

        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        self.btn_chat = ctk.CTkButton(self.sidebar, text="Chat", command=self.show_chat_list)
        self.btn_chat.pack(pady=10)

        self.btn_discover = ctk.CTkButton(self.sidebar, text="Discover")
        self.btn_discover.pack(pady=10)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", expand=True, fill="both")

        self.chat_users_frame = None
        self.chat_page_frame = None

        self.current_user = None
        self.show_chat_list()

    def show_chat_list(self):
        if self.chat_page_frame:
            self.chat_page_frame.destroy()

        if self.chat_users_frame:
            self.chat_users_frame.destroy()

        self.chat_users_frame = ctk.CTkFrame(self.main_frame)
        self.chat_users_frame.pack(expand=True, fill="both")

        users = self.logic.get_users()
        for user in users:
            ctk.CTkButton(self.chat_users_frame, text=f"{user['name']} ({'Online' if user['online'] else 'Offline'})", 
                          command=lambda u=user: self.open_chat(u)).pack(pady=5)

    def open_chat(self, user):
        self.current_user = user

        if self.chat_users_frame:
            self.chat_users_frame.destroy()

        if self.chat_page_frame:
            self.chat_page_frame.destroy()

        self.chat_page_frame = ctk.CTkFrame(self.main_frame)
        self.chat_page_frame.pack(expand=True, fill="both")

        top_bar = ctk.CTkFrame(self.chat_page_frame)
        top_bar.pack(fill="x")

        ctk.CTkButton(top_bar, text="Back", command=self.show_chat_list).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(top_bar, text=user['name']).pack(side="left", padx=5)
        ctk.CTkLabel(top_bar, text="Online" if user['online'] else "Offline", text_color="green" if user['online'] else "red").pack(side="left")

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
        print("Upload file clicked")  # Dummy handler

    def update_ui(self):
        if self.current_user:
            self.load_chat(self.current_user['id'])

if __name__ == '__main__':
    app = ChatApp()
    app.mainloop()
