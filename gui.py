# ui.py
import threading
import customtkinter as ctk
from service import ChatService, ConnectionSuccess, ConnectionFailure
from PIL import Image, ImageTk
import tkinter as tk
from models import User
import socket
import time

# Load icons
home_icon_white = ctk.CTkImage(Image.open("Assets/homeIconWhite.png"), size=(20, 20))
discover_icon_white = ctk.CTkImage(Image.open("Assets/discoverIconWhite.png"), size=(20, 20))

class ChatApp(ctk.CTk):
    def __init__(self):
        """Initialize the main window and all UI components."""
        super().__init__()
        self.title("PeerTalk")
        self.geometry("800x600")

        # Start the ChatService logic in a background thread
        self.logic = ChatService(ui_callback=self.handle_logic_callback)
        threading.Thread(target=self.logic.run, daemon=True).start()

        # Sidebar container for navigation buttons
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        # App title on the sidebar
        self.project_label = ctk.CTkLabel(self.sidebar, text="PeerTalk", font=ctk.CTkFont(size=20, weight="bold"))
        self.project_label.pack(pady=(30, 20))

        # Home button - shows list of chat users
        self.btn_home = ctk.CTkButton(
            self.sidebar,
            text="Home",
            image=home_icon_white,
            command=self.show_chat_list,
            fg_color="transparent",
            corner_radius=20,
            anchor="w",
            compound="left",
            width=200,
            height=40,
        )
        self.btn_home.pack(pady=0)

        # Discover button - placeholder for future feature
        self.btn_discover = ctk.CTkButton(
            self.sidebar,
            text="Discover",
            image=discover_icon_white,
            command=self.show_discover_page,
            fg_color="transparent",
            corner_radius=20,
            anchor="w",
            compound="left",
            width=200,
            height=40,
        )
        self.btn_discover.pack(pady=0)

        # Top frame for search box and info button
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent", bg_color="transparent")
        self.top_frame.pack(side="top", pady=20, padx=20)

        # Search box for filtering users by name
        self.search_entry = ctk.CTkEntry(
            self.top_frame,
            placeholder_text="Search",
            corner_radius=20,
            width=300,
            fg_color="transparent",
            bg_color="transparent"
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.show_chat_list())  # Run search on Enter
        self.search_entry.bind("<Escape>", lambda e: self.focus())  # Reset focus on Escape

        # Info button - opens info panel with local device details
        self.info_button = ctk.CTkButton(
            self.top_frame,
            text="i",
            width=30,
            height=30,
            corner_radius=30,
            fg_color="#3498db",
            hover_color="#2980b9",
            text_color="white",
            command=self.toggle_info_panel
        )
        self.info_button.pack(side="right")

        # Info panel (hidden by default)
        self.info_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        self.info_label = ctk.CTkLabel(self.info_frame, text="Device Name: Sample\nIP Address: 192.168.100.5")
        self.info_label.pack(padx=10, pady=5)
        self.info_frame.place_forget()  # Initially hidden

        # Main frame for dynamic content (chat list, chat page, etc.)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", expand=True, fill="both")

        # Get local IP address
        local_ip = socket.gethostbyname(socket.gethostname())

        # Create User object for the local device
        self.device_user = User(
            user_id="device_001",
            name="MyDevice",
            online=True,
            ip_address=local_ip,
            port=5050,
            connection_key="some_key"
        )

        # Initialize app state variables
        self.chat_users_frame = None
        self.chat_page_frame = None
        self.discover_frame = None
        self.current_user = None

        # Load the default chat list view
        self.show_chat_list()

    def toggle_info_panel(self):
        """
        Toggle the visibility of the info panel that shows local user/device information.
        """
        if self.info_frame.winfo_ismapped():
            # Hide the panel if it's already visible
            self.info_frame.place_forget()
        else:
            # Show the panel and update info
            self.update_idletasks()  # Ensures layout is updated before placement

            user = self.device_user
            if user:
                # Generate info string with user details
                info_text = (
                    f"User ID: {user.user_id}\n"
                    f"Name: {user.name}\n"
                    f"IP Address: {user.ip_address}\n"
                    f"Port: {user.port}"
                )
            else:
                info_text = "No user info available."

            self.info_label.configure(text=info_text)
            self.info_frame.update_idletasks()

            # Calculate position just below the info button
            x = self.info_button.winfo_rootx() - self.winfo_rootx()
            y = self.info_button.winfo_rooty() - self.winfo_rooty() + self.info_button.winfo_height()

            # Place and show the info panel
            self.info_frame.place(x=x - 50, y=y + 5)
            self.info_frame.lift()  # Ensure it appears on top of other widgets

    def show_chat_list(self):
        """
        Shows the chat list and restores the top bar (search box and info button).
        Ensures the top frame is correctly placed at the top with elements centered.
        """
        self.clear_main_frame()
        
        # Remove the top_frame from wherever it might be
        self.top_frame.pack_forget()
        
        # Clear any existing widgets in the top frame
        for widget in self.top_frame.winfo_children():
            widget.pack_forget()
        
        # Create a center container within the top frame
        center_container = ctk.CTkFrame(self.top_frame, fg_color="transparent", bg_color="transparent")
        center_container.pack(expand=True, fill="x")
        
        # Create a frame for search and info that will be centered
        search_info_frame = ctk.CTkFrame(center_container, fg_color="transparent", bg_color="transparent")
        search_info_frame.pack(side="top", pady=20, anchor="center")
        
        # Search box
        self.search_entry = ctk.CTkEntry(
            search_info_frame,
            placeholder_text="Search",
            corner_radius=20,
            width=300,
            fg_color="transparent",
            bg_color="transparent"
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.show_chat_list())
        self.search_entry.bind("<Escape>", lambda e: self.focus())
        
        # Info button
        self.info_button = ctk.CTkButton(
            search_info_frame,
            text="i",
            width=30,
            height=30,
            corner_radius=30,
            fg_color="#3498db",
            hover_color="#2980b9",
            text_color="white",
            command=self.toggle_info_panel
        )
        self.info_button.pack(side="right")
        
        # Ensure the top frame is properly placed at the top
        self.top_frame.pack(side="top", fill="x", before=self.main_frame)

        search_query = self.search_entry.get().lower().strip()
        all_users = self.logic.get_users()


        if search_query:
            users = [user for user in all_users if search_query in user["name"].lower()]
        else:
            users = all_users

        canvas = tk.Canvas(self.main_frame, bg="#2b2b2b", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        scrollbar = ctk.CTkScrollbar(self.main_frame, orientation="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = ctk.CTkFrame(canvas, fg_color="#2b2b2b")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_canvas_resize(event):
            canvas.itemconfig(window_id, width=event.width)

        canvas.bind("<Configure>", on_canvas_resize)

        for user in users:
            frame = ctk.CTkFrame(
                scrollable_frame,
                corner_radius=15,
                fg_color="#3c3f41"  # Darker gray or any color you prefer
            )

            frame.pack(fill="x", expand=True, pady=8, padx=10)

            status_color = "#27ae60" if user["online"] else "#c0392b"
            status_text = "Online" if user["online"] else "Offline"

            name_label = ctk.CTkLabel(
                frame,
                text=f"{user['name']} ({status_text})",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=status_color
            )
            name_label.pack(anchor="w", padx=10, pady=(8, 0))

            ip_label = ctk.CTkLabel(
                frame,
                text=f"IP: {user['ip_address']} • Port: {user['port']}",
                font=ctk.CTkFont(size=12),
                text_color="#bdc3c7"
            )
            ip_label.pack(anchor="w", padx=10, pady=(0, 8))

            chat_btn = ctk.CTkButton(
                frame,
                text="Open Chat",
                corner_radius=10,
                width=100,
                command=lambda u=user: self.open_chat(u)
            )
            chat_btn.pack(anchor="e", padx=10, pady=(0, 8))

    def open_chat(self, user):
        """
        Opens the chat interface for the selected user.
        Sets up the chat page layout, history panel, and message input area.
        Hides the search bar and info button during chat view.
        """
        # Hide the top frame (search bar and info button)
        self.top_frame.pack_forget()

        self.current_user = user
        self.clear_main_frame()

        # Frame that holds the entire chat page
        self.chat_page_frame = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b")
        self.chat_page_frame.pack(expand=True, fill="both")

        # Top bar: Back button, user name, online status
        top_bar = ctk.CTkFrame(self.chat_page_frame, fg_color="#3c3f41", corner_radius=10)
        top_bar.pack(fill="x", padx=20, pady=(20, 10))

        back_button = ctk.CTkButton(
            top_bar,
            text="← Back",
            width=80,
            command=self.show_chat_list,
            fg_color="#3498db",
            hover_color="#2980b9",
            corner_radius=10,
            text_color="white"
        )
        back_button.pack(side="left", padx=10, pady=5)

        ctk.CTkLabel(
            top_bar,
            text=user['name'],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=10)

        status_text = "Online" if user['online'] else "Offline"
        status_color = "#27ae60" if user['online'] else "#c0392b"

        ctk.CTkLabel(
            top_bar,
            text=status_text,
            font=ctk.CTkFont(size=14),
            text_color=status_color
        ).pack(side="left")

        # Chat message container (scrollable)
        chat_container = ctk.CTkFrame(self.chat_page_frame, fg_color="#2b2b2b")
        chat_container.pack(expand=True, fill="both", padx=20, pady=(0, 10))

        self.chat_history_frame = ctk.CTkScrollableFrame(
            chat_container,
            fg_color="#2b2b2b",
            corner_radius=10
        )
        self.chat_history_frame.pack(expand=True, fill="both")

        self.load_chat(user['id'])

        # Bottom bar: Message input and action buttons
        bottom_bar = ctk.CTkFrame(self.chat_page_frame, fg_color="#3c3f41", corner_radius=10)
        bottom_bar.pack(fill="x", padx=20, pady=(0, 20))

        self.message_entry = ctk.CTkEntry(
            bottom_bar,
            placeholder_text="Type your message...",
            corner_radius=10,
            width=300
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        self.message_entry.bind('<KeyRelease>', self.toggle_send_upload_buttons)

        self.upload_button = ctk.CTkButton(
            bottom_bar,
            text="Upload File",
            command=self.upload_file,
            fg_color="#f39c12",
            hover_color="#e67e22",
            text_color="white",
            corner_radius=10
        )
        self.upload_button.pack(side="right", padx=(5, 5), pady=10)

        self.send_button = ctk.CTkButton(
            bottom_bar,
            text="Send",
            command=self.send_message,
            state="disabled",
            fg_color="white",
            hover_color="#27ae60",
            text_color="black", 
            corner_radius=10
        )
        self.send_button.pack(side="right", padx=(5, 5), pady=10)

    def load_chat(self, user_id):
        """
        Loads chat messages for the given user ID into the chat history frame.
        Aligns messages to left or right based on sender.
        """
        # Clear previous messages
        for widget in self.chat_history_frame.winfo_children():
            widget.destroy()

        # Fetch message history from logic
        messages = self.logic.fetch_messages(user_id)

        for msg in messages:
            is_from_user = msg['from'] == user_id
            side = "w" if is_from_user else "e"
            bg_color = "#34495e" if is_from_user else "#16a085"
            text_color = "white"

            # Message bubble style
            bubble = ctk.CTkLabel(
                self.chat_history_frame,
                text=msg['message'],
                anchor=side,
                justify="left",
                wraplength=500,
                font=ctk.CTkFont(size=13),
                text_color=text_color,
                fg_color=bg_color,
                corner_radius=12,
                padx=10,
                pady=6
            )
            bubble.pack(anchor=side, padx=10, pady=4)

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
        elif result == 'peer_discovered':
            # Refresh UI from main thread
            self.after(100, self.refresh_peers)

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

    def start_discovery_session(self):
     if getattr(self, 'discovery_timer_active', False):
        return  # Already running
     self.discovery_started_at = time.time()
     self.discovery_timer_active = True
     self.check_discovery_timeout()


    def toggle_discovery(self):
        if self.discovery_switch.get():
            self.logic.start_discovery()

            self.options_frame.pack(fill="x", padx=10, pady=5)
            self.available_label.configure(text="Discovering peers...")
            self.available_label.pack(pady=(10, 0))
            self.available_list_frame.pack(fill="both", expand=True)

            self.start_discovery_session()

            self.refresh_peers()
        else:
            self.logic.stop_discovery()
            self.options_frame.pack_forget()
            self.available_label.pack_forget()
            self.available_list_frame.pack_forget()

    def refresh_peers(self):
     self.logic.stop_discovery()
     self.logic.start_discovery()

     self.available_label.configure(text="Discovering peers...")
     self.start_discovery_session()
     for widget in self.available_list_frame.winfo_children():
        widget.destroy()

     peers = self.logic.get_discovered_peers()
     if peers:
        self.available_label.configure(text="Available Peers:")
     else:
        if not getattr(self, 'discovery_timer_active', False):
            self.available_label.configure(text="No peers found ❌")

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

    def check_discovery_timeout(self):
     if not getattr(self, 'discovery_timer_active', False):
        return

     elapsed = time.time() - self.discovery_started_at
     if elapsed >= 10:
        self.discovery_timer_active = False
        self.logic.stop_discovery()
        peers = self.logic.get_discovered_peers()

        if not peers:
            self.available_label.configure(text="No peers found ❌")
        else:
            self.available_label.configure(text="Available Peers:")
            self.discovery_timer_active = False
     else:
        self.after(500, self.check_discovery_timeout)

if __name__ == '__main__':
    app = ChatApp()
    app.mainloop()
