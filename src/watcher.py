import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

class PDFHandler(FileSystemEventHandler):
    def __init__(self, callback, debounce_interval=2.0):
        """
        Args:
            callback (func): Function to call with the file path when a PDF is modified.
            debounce_interval (float): Time in seconds to wait after the last event before triggering.
        """
        self.callback = callback
        self.debounce_interval = debounce_interval
        self.pending_files = {} # {file_path: last_event_time}
        self.lock = threading.Lock()
        self.running = True
        
        # Start a single worker thread to check for stable files
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    def _process_queue(self):
        """Periodically checks pending files to see if they are ready to be processed."""
        while self.running:
            time.sleep(1.0) # Check every second
            now = time.time()
            
            with self.lock:
                files_to_process = []
                # Check for files that have passed the debounce interval
                for file_path, last_time in list(self.pending_files.items()):
                    if now - last_time >= self.debounce_interval:
                        files_to_process.append(file_path)
                        del self.pending_files[file_path]
            
            # Process outside the lock
            for file_path in files_to_process:
                self._trigger(file_path)

    def _trigger(self, file_path):
        """Trigger the callback."""
        try:
            self.callback(file_path)
        except Exception as e:
            logging.exception(f"Error processing {file_path}: {e}")

    def on_modified(self, event):
        if event.is_directory:
            return
        
        filename = event.src_path
        if not filename.lower().endswith('.pdf'):
            return
            
        # Ignore temp files (libreoffice lock files, etc.)
        if Path(filename).name.startswith('.~lock'):
            return

        logging.info(f"File modified detected: {filename}")
        
        with self.lock:
            self.pending_files[filename] = time.time() # Update timestamp

    def on_created(self, event):
        # Treat creation same as modification for our purposes
        self.on_modified(event)

    def on_moved(self, event):
        if event.is_directory:
            return
        
        filename = event.dest_path
        if not filename.lower().endswith('.pdf'):
            return
            
        if Path(filename).name.startswith('.~lock'):
            return

        logging.info(f"File moved/renamed detected: {filename}")
        with self.lock:
            self.pending_files[filename] = time.time()
            
    def stop(self):
        self.running = False


class SystemWatcher:
    def __init__(self, pdf_folder, callback):
        self.pdf_folder = pdf_folder
        self.callback = callback
        self.observer = Observer()
        self.handler = PDFHandler(callback)

    def start(self):
        if not Path(self.pdf_folder).exists():
            logging.warning(f"Watch folder does not exist: {self.pdf_folder}")
            return

        logging.info(f"Starting SystemWatcher on: {self.pdf_folder}")
        self.observer.schedule(self.handler, self.pdf_folder, recursive=False)
        self.observer.start()

    def stop(self):
        logging.info("Stopping SystemWatcher...")
        self.handler.stop()
        self.observer.stop()
        self.observer.join()
