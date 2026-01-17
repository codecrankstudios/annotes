import time
import logging
import sys
from pathlib import Path

# Add src to path just in case
sys.path.insert(0, str(Path(__file__).parent))

import settings
import annotes
from watcher import SystemWatcher

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("watcher_service.log")
        ]
    )

    logging.info("Initializing configuration...")
    settings.initialize()

    pdf_folder = settings.CONFIG.get("pdf_folder")
    if not pdf_folder:
        logging.error("No 'pdf_folder' configured in config.yaml. Exiting.")
        sys.exit(1)

    logging.info(f"Target PDF folder: {pdf_folder}")

    def on_file_change(file_path):
        logging.info(f"Detected change in: {file_path}. Processing...")
        try:
            annotes.process_pdf(file_path)
            logging.info(f"Successfully processed: {file_path}")
        except Exception as e:
            logging.error(f"Failed to process {file_path}: {e}")

    watcher = SystemWatcher(pdf_folder, on_file_change)
    
    try:
        watcher.start()
        logging.info("Watcher service is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping watcher...")
        watcher.stop()
    except Exception as e:
        logging.error(f"Watcher crashed: {e}")
        watcher.stop()

if __name__ == "__main__":
    main()
