import customtkinter as ctk
import threading
import os
import platform
import subprocess
from tkinter import filedialog
from downloader import YouTubeDownloader
import requests
from PIL import Image, ImageTk
from io import BytesIO

# --- App Theme Colors ---
BG_COLOR = "#09090E"           # Deep space black
CARD_COLOR = "#15151F"         # Slightly lighter for cards
SURFACE_COLOR = "#20202D"      # For entries and inactive elements
ACCENT_COLOR = "#6D28D9"       # Vibrant Nebula Purple
ACCENT_HOVER = "#5B21B6"       # Darker purple for hover
TEXT_MAIN = "#F8FAFC"          # Crisp white
TEXT_SUB = "#94A3B8"           # Slate gray for secondary text
SUCCESS_COLOR = "#10B981"      # Emerald green
ERROR_COLOR = "#EF4444"        # Red

class NebulaDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("Nebula Downloader")
        self.geometry("900x750")
        self.configure(fg_color=BG_COLOR) 
        self.minsize(800, 700)
        
        # Center window on screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Initialize Downloader Engine
        self.downloader = YouTubeDownloader(progress_callback=self.update_progress)

        # --- Fonts ---
        self.font_title = ctk.CTkFont(family="Segoe UI Variable Display", size=32, weight="bold")
        self.font_subtitle = ctk.CTkFont(family="Segoe UI", size=14)
        self.font_body = ctk.CTkFont(family="Segoe UI", size=13)
        self.font_bold = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")

        # --- Main Container ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=40, pady=30)

        # Header
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(self.header_frame, text="🌌 NEBULA", font=self.font_title, text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkLabel(self.header_frame, text="High-Performance Media Engine", font=self.font_subtitle, text_color=TEXT_SUB).pack(side="left", padx=15, pady=(12, 0))

        # ==========================================
        # CARD 1: SEARCH & INPUT
        # ==========================================
        self.search_card = ctk.CTkFrame(self.main_container, fg_color=CARD_COLOR, corner_radius=16)
        self.search_card.pack(fill="x", pady=(0, 15))

        self.input_frame = ctk.CTkFrame(self.search_card, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=20, pady=20)

        self.url_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Paste YouTube URL or enter search term...", 
            height=45, 
            fg_color=SURFACE_COLOR, 
            border_width=0, 
            font=self.font_body,
            text_color=TEXT_MAIN,
            corner_radius=8
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.clear_btn = ctk.CTkButton(
            self.input_frame, 
            text="✕", 
            width=45, 
            height=45, 
            fg_color=SURFACE_COLOR, 
            hover_color="#333345", 
            font=self.font_bold,
            corner_radius=8,
            command=self.clear_search
        )
        self.clear_btn.pack(side="left", padx=(0, 10))

        self.search_btn = ctk.CTkButton(
            self.input_frame, 
            text="🔍 Search", 
            width=120, 
            height=45, 
            fg_color=ACCENT_COLOR, 
            hover_color=ACCENT_HOVER, 
            font=self.font_bold,
            corner_radius=8,
            command=self.start_search
        )
        self.search_btn.pack(side="right")

        # --- Search Results Panel (Hidden by default) ---
        self.results_frame = ctk.CTkScrollableFrame(
            self.search_card, 
            fg_color=BG_COLOR, 
            corner_radius=8, 
            height=200
        )

        # ==========================================
        # CARD 2: CONFIGURATION
        # ==========================================
        self.config_card = ctk.CTkFrame(self.main_container, fg_color=CARD_COLOR, corner_radius=16)
        self.config_card.pack(fill="x", pady=(0, 15))
        
        self.config_grid = ctk.CTkFrame(self.config_card, fg_color="transparent")
        self.config_grid.pack(fill="x", padx=20, pady=20)
        self.config_grid.columnconfigure(1, weight=1)

        # Row 0: Save Location
        ctk.CTkLabel(self.config_grid, text="📂 Save to:", font=self.font_bold, text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w", pady=(0, 15), padx=(0, 15))
        
        self.path_frame = ctk.CTkFrame(self.config_grid, fg_color="transparent")
        self.path_frame.grid(row=0, column=1, sticky="we", pady=(0, 15))
        
        self.path_var = ctk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.path_entry = ctk.CTkEntry(
            self.path_frame, 
            textvariable=self.path_var,
            height=35, 
            fg_color=SURFACE_COLOR, 
            border_width=0, 
            font=self.font_body,
            text_color=TEXT_SUB,
            corner_radius=6
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.path_btn = ctk.CTkButton(
            self.path_frame, 
            text="Browse", 
            width=80, 
            height=35, 
            fg_color=SURFACE_COLOR, 
            hover_color="#333345", 
            font=self.font_body,
            corner_radius=6,
            command=self.browse_folder
        )
        self.path_btn.pack(side="right")

        # Row 1: Format & Quality
        ctk.CTkLabel(self.config_grid, text="⚙️ Format:", font=self.font_bold, text_color=TEXT_MAIN).grid(row=1, column=0, sticky="w", pady=(0, 15), padx=(0, 15))
        
        self.format_frame = ctk.CTkFrame(self.config_grid, fg_color="transparent")
        self.format_frame.grid(row=1, column=1, sticky="w", pady=(0, 15))

        self.mode_var = ctk.StringVar(value="Video")
        self.mode_switch = ctk.CTkSegmentedButton(
            self.format_frame, 
            values=["Video", "Audio"], 
            command=self.toggle_mode,
            selected_color=ACCENT_COLOR,
            selected_hover_color=ACCENT_HOVER,
            unselected_color=SURFACE_COLOR,
            unselected_hover_color="#333345",
            font=self.font_bold,
            height=32
        )
        self.mode_switch.pack(side="left", padx=(0, 15))
        self.mode_switch.set("Video")

        self.quality_var = ctk.StringVar(value="Best")
        self.quality_menu = ctk.CTkOptionMenu(
            self.format_frame, 
            values=["Best", "1080p", "720p", "480p"], 
            variable=self.quality_var,
            fg_color=SURFACE_COLOR, 
            button_color=SURFACE_COLOR,
            button_hover_color="#333345",
            dropdown_fg_color=SURFACE_COLOR,
            dropdown_hover_color=ACCENT_COLOR,
            font=self.font_body,
            height=32,
            width=150
        )
        self.quality_menu.pack(side="left")

        # Row 2: Playlist
        ctk.CTkLabel(self.config_grid, text="📑 Batch:", font=self.font_bold, text_color=TEXT_MAIN).grid(row=2, column=0, sticky="w", padx=(0, 15))
        self.playlist_var = ctk.BooleanVar(value=False)
        self.playlist_switch = ctk.CTkSwitch(
            self.config_grid, 
            text="Download Entire Playlist", 
            variable=self.playlist_var,
            progress_color=ACCENT_COLOR,
            font=self.font_body,
            text_color=TEXT_SUB
        )
        self.playlist_switch.grid(row=2, column=1, sticky="w")

        # ==========================================
        # CARD 3: ACTION & STATUS
        # ==========================================
        self.action_card = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.action_card.pack(fill="both", expand=True)

        self.buttons_frame = ctk.CTkFrame(self.action_card, fg_color="transparent")
        self.buttons_frame.pack(pady=(20, 15))

        self.download_btn = ctk.CTkButton(
            self.buttons_frame, 
            text="⬇️ START DOWNLOAD", 
            height=55, 
            width=280, 
            fg_color=TEXT_MAIN, 
            text_color=BG_COLOR,
            hover_color="#E2E8F0", 
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            corner_radius=28,
            command=self.start_download
        )
        self.download_btn.pack(side="left", padx=10)

        self.cancel_btn = ctk.CTkButton(
            self.buttons_frame, 
            text="✕ Cancel", 
            height=55, 
            width=120, 
            fg_color=SURFACE_COLOR, 
            hover_color="#333345", 
            font=self.font_bold,
            corner_radius=28,
            command=self.cancel_download,
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=10)

        self.progress_bar = ctk.CTkProgressBar(
            self.action_card, 
            width=500, 
            height=8, 
            progress_color=ACCENT_COLOR,
            fg_color=SURFACE_COLOR
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(10, 5))

        self.status_label = ctk.CTkLabel(
            self.action_card, 
            text="Ready to launch...", 
            font=self.font_body, 
            text_color=TEXT_SUB
        )
        self.status_label.pack()

        self.check_ffmpeg()

    # --- Methods (Logic remains completely untouched to ensure compatibility) ---

    def check_ffmpeg(self):
        if self.downloader.ffmpeg_path is None:
            self.status_label.configure(
                text="⚠️ FFmpeg NOT FOUND! High quality/MP3 will fail.", 
                text_color="#F59E0B" # Amber color
            )

    def toggle_mode(self, value):
        self.mode_var.set(value)
        if value == "Video":
            self.quality_menu.configure(values=["Best", "1080p", "720p", "480p"])
            self.quality_var.set("Best")
        else:
            self.quality_menu.configure(values=["High (320kbps)", "Medium (192kbps)", "Low (128kbps)"])
            self.quality_var.set("High (320kbps)")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def clear_search(self):
        self.url_entry.delete(0, "end")
        self.results_frame.pack_forget()
        self.status_label.configure(text="Search cleared", text_color=TEXT_SUB)

    def cancel_download(self):
        self.downloader.cancel_requested = True
        self.status_label.configure(text="Cancelling... please wait", text_color="#F59E0B")

    def update_progress(self, value):
        self.after(0, lambda: self._do_update_progress(value))

    def _do_update_progress(self, value):
        if isinstance(value, str):
            self.status_label.configure(text=value, text_color=TEXT_MAIN)
        else:
            self.progress_bar.set(value / 100)
            self.status_label.configure(text=f"Downloading... {int(value)}%", text_color=TEXT_MAIN)

    def start_search(self):
        query = self.url_entry.get().strip()
        if not query:
            self.status_label.configure(text="Please enter a search term", text_color=ERROR_COLOR)
            return

        self.status_label.configure(text="Searching YouTube...", text_color=TEXT_MAIN)
        self.search_btn.configure(state="disabled")
        threading.Thread(target=self.perform_search, args=(query,), daemon=True).start()

    def perform_search(self, query):
        if query.startswith(("http://", "https://")):
            try:
                info = self.downloader.get_info(query)
                results = [(info['title'], info['webpage_url'] if 'webpage_url' in info else query, info['thumbnail'])]
            except Exception as e:
                results = []
        else:
            results = self.downloader.search_youtube(query)
        self.after(0, lambda: self.display_results(results))

    def display_results(self, results):
        self.search_btn.configure(state="normal")
        if not results:
            self.status_label.configure(text="No results found", text_color=ERROR_COLOR)
            return
        
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        for title, url, thumb_url in results:
            res_card = ctk.CTkFrame(self.results_frame, fg_color=SURFACE_COLOR, corner_radius=8)
            res_card.pack(fill="x", pady=4, padx=4)
            
            thumb_label = ctk.CTkLabel(res_card, text="...", width=80, height=45, fg_color=BG_COLOR, corner_radius=4)
            thumb_label.pack(side="left", padx=8, pady=8)
            
            btn = ctk.CTkButton(
                res_card, 
                text=title, 
                fg_color="transparent", 
                text_color=TEXT_MAIN, 
                anchor="w", 
                font=self.font_body,
                hover_color="#333345",
                command=lambda u=url, t=title: self.select_result(u, t)
            )
            btn.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=8)
            
            threading.Thread(target=self.load_thumbnail, args=(thumb_url, thumb_label), daemon=True).start()
            
        self.results_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.status_label.configure(text="Select a video from the list", text_color=ACCENT_COLOR)

    def load_thumbnail(self, url, label):
        try:
            with requests.get(url, timeout=5) as response:
                response.raise_for_status()
                img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img.thumbnail((80, 45))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 45))
            self.after(0, lambda: label.configure(image=ctk_img, text=""))
        except Exception:
            self.after(0, lambda: label.configure(text="No Image", text_color=TEXT_SUB))

    def select_result(self, url, title):
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url)
        self.results_frame.pack_forget()
        self.status_label.configure(text=f"Selected: {title[:50]}...", text_color=ACCENT_COLOR)

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.configure(text="Please provide a URL or search for a video", text_color=ERROR_COLOR)
            return
            
        mode = self.mode_var.get()
        quality = self.quality_var.get()
        do_playlist = self.playlist_var.get()
        
        self.download_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.status_label.configure(text="Initializing download...", text_color=TEXT_MAIN)
        self.downloader.cancel_requested = False
        self.progress_bar.set(0)
        
        threading.Thread(target=self.run_download, args=(url, mode, quality, do_playlist), daemon=True).start()

    def run_download(self, url, mode, quality, do_playlist):
        try:
            save_path = self.path_var.get()
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)
                
            if do_playlist:
                self.downloader.download_playlist(url, mode, quality, save_path)
            elif mode == "Video":
                self.downloader.download_video(url, quality, save_path)
            else:
                self.downloader.download_audio(url, quality, save_path)
                
            self.after(0, lambda: self.status_label.configure(text="Download Complete! 🎉", text_color=SUCCESS_COLOR))
            self.after(0, lambda: self.open_download_folder(save_path))
            self.after(0, lambda: self.progress_bar.set(1))
            
        except Exception as e:
            error_msg = str(e)
            if "cancelled" in error_msg.lower():
                self.after(0, lambda: self.status_label.configure(text="Download Cancelled 🛑", text_color=ERROR_COLOR))
            else:
                self.after(0, lambda: self.status_label.configure(text=f"Error: {error_msg[:50]}...", text_color=ERROR_COLOR))
            self.after(0, lambda: self.progress_bar.set(0))
            
        finally:
            self.after(0, lambda: self.download_btn.configure(state="normal"))
            self.after(0, lambda: self.cancel_btn.configure(state="disabled"))

    def open_download_folder(self, path):
        """Open the folder in the OS file explorer."""
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            print(f"Could not open folder: {e}")

if __name__ == "__main__":
    app = NebulaDownloader()
    app.mainloop()