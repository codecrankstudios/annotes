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
        """Load icon or generate default."""
        # Use settings.get_resource_path to find icon in bundle
        icon_path = settings.get_resource_path("app_icon.png")
        
        if icon_path.exists():
            return Image.open(icon_path)
        
        # Generate default icon
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), (79, 195, 247))
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill=(30, 30, 30))
        return image

    def start_watcher(self):
        pdf_folder = settings.CONFIG.get("pdf_folder")
        if pdf_folder and Path(pdf_folder).exists():
            self.watcher = SystemWatcher(pdf_folder, self.on_file_changed)
            self.watcher.start()
            print(f"Watcher started on: {pdf_folder}")
        else:
            print("Watcher not started: Invalid PDF folder.")

    def on_file_changed(self, file_path):
        """Callback from Watchdog thread."""
        try:
            status = annotes.process_pdf(file_path)
            basename = os.path.basename(file_path)
            self.send_notification(f"Processed: {basename}", status or "Done")
        except Exception as e:
            print(f"Error processing file: {e}")

    def send_notification(self, title, message):
        if self.icon:
            # Pystray notification support varies by OS
            try:
                self.icon.notify(message, title)
            except Exception:
                print(f"Notification: {title} - {message}")

    def scan_now(self, icon, item):
        print("🔍 Manual Scan Initiated...")
        threading.Thread(target=self._run_scan, daemon=True).start()

    def _run_scan(self):
        annotes.main()
        self.send_notification("Annotes", "Manual Scan Complete")

    def open_dashboard(self, icon, item):
        web_ui.open_dashboard()

    def open_help(self, icon, item):
        webbrowser.open("http://127.0.0.1:8080/help")

    def quit_app(self, icon, item):
        print("Shutting down...")
        self.remove_lock()
        if self.watcher:
            self.watcher.stop()
        icon.stop()
        sys.exit(0)

    def run(self):
        menu = pystray.Menu(
            item('Scan Now', self.scan_now),
            item('Docs & Web Settings', self.open_dashboard),
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

        self.icon.run()

if __name__ == "__main__":
    app = TrayApp()
    app.run()
