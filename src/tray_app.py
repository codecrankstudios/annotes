import sys
import os
import threading
import time
import webbrowser
from pathlib import Path
import signal

from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# Add local src to path
sys.path.insert(0, str(Path(__file__).parent))

import settings
import annotes
import web_ui
from watcher import SystemWatcher

class TrayApp:
    def __init__(self):
        # Initialize Settings & Logging FIRST to ensure paths are set
        settings.initialize()
        annotes.setup_logging()

        # Use User Data Dir for lock file (persistent path), not temp bundle path
        self.lock_file = settings.USER_DATA_DIR / "annotes.lock"
        
        # Single Instance Lock
        if self.check_lock():
            print(f"❌ Annotes is already running (PID: {self.get_lock_pid()}).")
            print("💡 Tip: Use 'pkill -f tray_app.py' to stop the background process.")
            sys.exit(0)
        
        self.watcher = None
        self.icon = None

        # Start Web Server Thread
        self.web_server_thread = threading.Thread(target=web_ui.run_server, daemon=True)
        self.web_server_thread.start()
        
        # Start Watcher
        self.start_watcher()

    def get_lock_pid(self):
        try: return self.lock_file.read_text().strip()
        except: return "?"

    def check_lock(self):
        """Simple lock file check."""
        if self.lock_file.exists():
            try:
                pid = int(self.lock_file.read_text().strip())
                os.kill(pid, 0)
                return True
            except (OSError, ValueError):
                print("⚠️ Found stale lock file. Taking ownership.")
        
        self.lock_file.write_text(str(os.getpid()))
        return False

    def remove_lock(self):
        if self.lock_file.exists():
            try:
                if self.lock_file.read_text().strip() == str(os.getpid()):
                    os.remove(self.lock_file)
            except: pass

    def create_image(self):
        """Load icon or generate default, ensured for tray sizes."""
        icon_path = settings.get_resource_path("app_icon.png")
        icon_path_alt = settings.get_resource_path("logo.png")
        
        image = None
        if icon_path.exists():
            try:
                image = Image.open(icon_path)
            except Exception as e:
                print(f"⚠️ Error loading app_icon.png: {e}")
        
        if not image and icon_path_alt.exists():
            try:
                image = Image.open(icon_path_alt)
            except Exception as e:
                print(f"⚠️ Error loading logo.png: {e}")

        if image:
            # Resize for tray compatibility (many Linux backends fail with large icons)
            # Use Resampling.LANCZOS if available, else ANTIALIAS
            try:
                sampling = Image.Resampling.LANCZOS
            except AttributeError:
                sampling = Image.ANTIALIAS
            
            image = image.resize((64, 64), sampling)
            return image.convert("RGBA")
        
        # Enhanced Fallback icon
        print("ℹ️ Using fallback icon (could not find/load app_icon.png)")
        width, height = 64, 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0)) # Transparent background
        dc = ImageDraw.Draw(image)
        # Draw a rounded blue square as background
        dc.rounded_rectangle((4, 4, 60, 60), radius=12, fill=(79, 195, 247, 255))
        # Draw a white 'A' in the middle
        dc.text((20, 10), "A", fill=(255, 255, 255, 255))
        return image

    def start_watcher(self):
        pdf_folder = settings.CONFIG.get("pdf_folder")
        if pdf_folder and Path(pdf_folder).exists():
            try:
                self.watcher = SystemWatcher(pdf_folder, self.on_file_changed)
                self.watcher.start()
                print(f"✅ Watcher started on: {pdf_folder}")
            except Exception as e:
                print(f"❌ Failed to start watcher: {e}")
        else:
            print(f"⚠️ Watcher not started: Invalid or missing PDF folder ('{pdf_folder}')")

    def on_file_changed(self, file_path):
        """Callback from Watchdog thread."""
        try:
            status = annotes.process_pdf(file_path)
            basename = os.path.basename(file_path)
            print(f"Sync complete: {basename} ({status or 'Done'})")
            self.send_notification(f"Processed: {basename}", status or "Done")
        except Exception as e:
            print(f"Error processing file: {e}")

    def send_notification(self, title, message):
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception:
                print(f"Notification: {title} - {message}")

    def scan_now(self, icon, item):
        print("🔍 Manual Scan Initiated...")
        threading.Thread(target=self._run_scan, daemon=True).start()

    def _run_scan(self):
        try:
            annotes.main()
            self.send_notification("Annotes", "Manual Scan Complete")
        except Exception as e:
            print(f"Scan failed: {e}")

    def open_dashboard(self, icon=None, item=None):
        print("🌐 Opening Dashboard...")
        web_ui.open_dashboard()

    def open_help(self, icon=None, item=None):
        webbrowser.open("http://127.0.0.1:8080/help")

    def quit_app(self, icon, item):
        print("🛑 Shutting down Annotes...")
        self.remove_lock()
        if self.watcher:
            self.watcher.stop()
        if self.icon:
            self.icon.stop()
        sys.exit(0)

    def run(self):
        # Define menu items
        menu = pystray.Menu(
            item('Scan Now', self.scan_now),
            item('Docs & Web Settings', self.open_dashboard, default=True),
            item('User Manual', self.open_help),
            pystray.Menu.SEPARATOR,
            item('Quit', self.quit_app)
        )

        self.icon = pystray.Icon(
            "Annotes", 
            self.create_image(), 
            "Annotes: Watching PDFs", 
            menu
        )
        
        # Register signal handlers for clean exit on Ctrl+C
        signal.signal(signal.SIGINT, lambda s, f: self.quit_app(self.icon, None))
        signal.signal(signal.SIGTERM, lambda s, f: self.quit_app(self.icon, None))

        print("🚀 Annotes Tray App is running. Right-click the icon to manage.")
        self.icon.run()


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Annotes: Tray Application")
    parser.add_argument("--init", action="store_true", help="Initialize configuration and base folders")
    args = parser.parse_args()

    if args.init:
        print("🛠️  Annotes Initialization & Setup")
        settings.initialize()
        print(f"✅ Configuration directory: {settings.USER_DATA_DIR}")
        print(f"📁 PDF Folder: {settings.CONFIG['pdf_folder']}")
        print(f"📁 Notes Folder: {settings.CONFIG['notes_folder']}")
        print("\n🚀 Installation / Setup complete.")
        sys.exit(0)

    app = TrayApp()
    app.run()

