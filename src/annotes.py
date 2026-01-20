import os
import logging
from pathlib import Path
import settings
from utils import get_datetime_str, get_pdf_files, annotation_filename
from pdfutils import PdfUtils as pdfutils
from mdutils import MarkdownBuilder as mdb
from formatter import render_page_annotations
from connectors import ConnectorFactory

# Initialize settings if not already done
if not settings.CONFIG:
    settings.initialize()

from collections import deque
import logging

# In-memory log buffer for the dashboard (keeps last 50 events)
LOG_BUFFER = deque(maxlen=50)

def setup_logging():
    """Configures logging to file and memory buffer."""
    # Reset handlers if re-initializing
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    # 1. File Handler (app.log)
    # Use persistent log path from settings
    log_file = settings.USER_DATA_DIR / "app.log"
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    
    # 2. Memory Handler (for Dashboard)
    class DequeHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            LOG_BUFFER.append(log_entry)
            
    mem_handler = DequeHandler()
    mem_handler.setLevel(logging.INFO)
    mem_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, mem_handler]
    )

def get_recent_logs():
    """Returns list of recent log entries from memory."""
    return list(LOG_BUFFER)

def write_notes_log(message: str, notes_folder: str = None) -> None:
    """Append a timestamped message to the notes-folder log file (Permanent History)."""
    if not notes_folder:
        notes_folder = settings.CONFIG.get("notes_folder")
        
    try:
        # Also log to main app log so it shows in dashboard
        logging.info(f"Synced: {message}")
        
        if notes_folder:
            log_path = Path(notes_folder) / "annotes.log"
            with open(log_path, "a", encoding="utf-8") as nf:
                nf.write(f"{get_datetime_str()} - {message}\n")
    except Exception:
        pass # Logging failure shouldn't crash app

def process_pdf(pdf_path: str):
    """
    Main entry point to process a single PDF file.
    Triggers parsing, image extraction, formatting, and connector output.
    """
    pdf_path = str(pdf_path) # Ensure string
    pdf_basename = os.path.basename(pdf_path)
    
    # Reload config to ensure fresh settings (e.g. if user changed config)
    # settings.initialize() # simple reload might be enough
    
    logging.info("Processing PDF: %s", pdf_basename)
    
    try:
        doc = pdfutils.open_pdf(pdf_path)
    except Exception as e:
        logging.exception("Failed to open PDF %s: %s", pdf_path, e)
        return

    # 1. Parse Annotations
    if not pdfutils.check_annotations(doc):
        logging.info("No annotations found in %s", pdf_basename)
        try: doc.close() 
        except Exception as e: logging.warning(f"Error closing doc {pdf_basename}: {e}")
        return "skipped: no annotations"

    # Use the new extraction logic
    pdf_util_instance = pdfutils(doc) # This parses annotations in __init__
    parsed_annots = pdf_util_instance.annotations
    
    if not parsed_annots:
        logging.info("No annotations found (post-parse) in %s", pdf_basename)
        doc.close()
        return "skipped: parsed_annots empty"

    notes_folder = settings.CONFIG.get("notes_folder")
    if not os.path.exists(notes_folder):
        os.makedirs(notes_folder)

    # 2. Extract Images (Pre-processing)
    # We need to extract images before rendering so we can link to them.
    image_counter = 1
    for annot_data in parsed_annots:
        if annot_data.get("type") == "Image":
            rect = annot_data.get("rect")
            content = annot_data.get("comment")
            page_num = annot_data.get("page")
            
            # Get actual page object
            # Note: page_num in dict is 1-based, doc index is 0-based
            page = doc[page_num - 1]
            
            # Call extract_image_from_annot
            # It returns updated image_counter
            image_counter = pdfutils.extract_image_from_annot(
                rect, content, page, pdf_basename, notes_folder, image_counter
            )

    # 3. Build Markdown
    annotated_doc = mdb()
    
    # Front Matter
    annotated_file_name, annotated_file_path = annotation_filename(pdf_basename=pdf_basename)
    # Note: annotated_file_path comes from utils which uses default notes_folder. 
    # Connectors might override this, but FileConnector needs a path.
    
    fm_settings = settings.CONFIG["output_settings"].get("yaml_front_matter_settings", {})
    if fm_settings.get("include_yaml_front_matter", False):
        fm = {}
        keys = fm_settings.get("yaml_front_matter_keys", [])
        if "title" in keys: fm["title"] = annotated_file_name
        if "created" in keys: fm["created"] = get_datetime_str()
        if "modified" in keys: fm["modified"] = get_datetime_str()
        if "tags" in keys: fm["tags"] = settings.CONFIG["output_settings"].get("annotated_file_tags", [])
        annotated_doc.add_yaml_front_matter(fm)

    # Title
    annotated_doc.add_heading(annotated_file_name, level=1)
    
    # Render Body
    # We group by page to use render_page_annotations which iterates over annots
    # But render_page_annotations filters annots by page_num? Yes, I added that.
    # So we can just iterate pages and pass ALL parsed_annots.
    
    for page in doc:
        # render_page_annotations expects parsed dicts list
        render_page_annotations(
            page.number + 1,
            parsed_annots,
            annotated_doc,
            settings.CONFIG,
            pdf_basename=pdf_basename
        )

    # 4. Push to Connectors
    full_markdown = annotated_doc.content
    logging.info(f"Generated Markdown length: {len(full_markdown)} chars")
    
    connectors = ConnectorFactory.get_connectors(settings.CONFIG)
    
    for connector in connectors:
        logging.info(f"Pushing to connector: {type(connector).__name__} OutputPath: {annotated_file_path}")
        connector.push_note(
            title=annotated_file_name,
            content=full_markdown,
            output_path=annotated_file_path 
        )
    
    write_notes_log(f"Synced: {pdf_basename} -> {annotated_file_path}", notes_folder)
    doc.close()

def main():
    setup_logging()
    # Manual scan of all files
    pdf_folder = Path(settings.CONFIG.get("pdf_folder"))
    pdf_files = get_pdf_files(pdf_folder)
    
    print(f"Scanning {len(pdf_files)} PDF files in {pdf_folder}...")
    for f in pdf_files:
        status = process_pdf(f)
        if status:
             print(f"Processed {f}: {status}")

if __name__ == "__main__":
    main()
