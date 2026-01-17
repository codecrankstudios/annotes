import sys
import os
import time
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pdfutils
from annotes import process_pdf
from watcher import SystemWatcher
from connectors import FileConnector

logging.basicConfig(level=logging.INFO)

def test_full_pipeline():
    print("\n--- Testing Full Pipeline with Real PDF ---")
    import pymupdf
    import shutil
    
    # Create temp dir
    import tempfile
    
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        pdf_path = tmp_dir / "test_annotation.pdf"
        
        # Create PDF with annotations
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((50, 50), "This is some text to highlight.")
        
        # Add Highlight
        r1 = pymupdf.Rect(50, 40, 200, 60)
        annot1 = page.add_highlight_annot(r1)
        annot1.set_info(content="My Highlight Comment")
        annot1.update()
        
        # Add Square (Image)
        r2 = pymupdf.Rect(50, 100, 150, 200)
        annot2 = page.add_rect_annot(r2)
        annot2.set_info(content="My Image Capture")
        annot2.update()
        
        doc.save(str(pdf_path))
        doc.close()
        print(f"Created annotated PDF at {pdf_path}")
        
        # Run process_pdf
        # We need to mock settings to point to this temp dir for output
        import settings
        # Initialize if not already
        if not settings.CONFIG:
             # minimal config
             settings.CONFIG = {
                 "notes_folder": str(tmp_dir / "notes"),
                 "output_settings": {
                     "yaml_front_matter_settings": {"include_yaml_front_matter": True},
                     "page_link_settings": {"include_page_links": True},
                     "annotated_file_prefix": "", 
                     "annotated_file_suffix": ""
                 },
                 "connectors": [{"type": "file"}]
             }
        else:
            # Override notes folder and force prefixes
             settings.CONFIG["notes_folder"] = str(tmp_dir / "notes")
             settings.CONFIG["output_settings"]["annotated_file_prefix"] = ""
             settings.CONFIG["output_settings"]["annotated_file_suffix"] = ""

        print("Running process_pdf...")
        process_pdf(pdf_path)
        print("process_pdf completed successfully.")
        
        # Verify output
        output_file = tmp_dir / "notes" / "test_annotation.md"
        if output_file.exists():
            print(f"Output markdown created: {output_file}")
            content = output_file.read_text()
            print("Content preview:")
            print(content[:200])
            if "My Highlight Comment" in content:
                print("SUCCESS: Highlight comment found.")
            else:
                print("FAILURE: Highlight comment NOT found.")
                
            assets_dir = tmp_dir / "notes" / "assets" / "test_annotation.pdf"
            if assets_dir.exists() and list(assets_dir.glob("*.png")):
                 print(f"SUCCESS: Image assets generated in {assets_dir}")
            else:
                 print(f"FAILURE: No image assets found in {assets_dir}")

        else:
            print(f"FAILURE: Output markdown NOT created at {output_file}")
            print("Contents of notes folder:")
            for f in (tmp_dir / "notes").iterdir():
                print(f" - {f.name}")

    except Exception as e:
        print(f"EXCEPTION during pipeline test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)

def test_existing_files():
    print("\n--- Testing Existing PDFs in test/ folder ---")
    test_dir = Path(__file__).parent
    pdf_files = list(test_dir.glob("*.pdf"))
    
    # Filter out lock files
    pdf_files = [p for p in pdf_files if not p.name.startswith(".~lock")]
    
    if not pdf_files:
        print("No PDF files found in test/ folder.")
        return

    # Mock settings to output to test/notes_output
    import settings
    output_dir = test_dir / "notes_output"
    if not output_dir.exists():
        output_dir.mkdir()
        
    settings.CONFIG = {
         "notes_folder": str(output_dir),
         "output_settings": {
             "yaml_front_matter_settings": {"include_yaml_front_matter": True},
             "page_link_settings": {"include_page_links": True},
             "annotated_file_prefix": "Notes - ", 
             "annotated_file_suffix": ""
         },
         "markdown_settings": {
              "tab_size": 4
         },
         "connectors": [{"type": "file"}]
    }

    for pdf in pdf_files:
        print(f"Processing: {pdf.name}")
        try:
            process_pdf(str(pdf))
            print(f"  > Completed {pdf.name}")
            
            # Check for output
            expected_name = f"Notes - {pdf.stem}.md"
            expected_path = output_dir / expected_name
            if expected_path.exists():
                print(f"  > SUCCESS: Output found at {expected_path}")
            else:
                print(f"  > FAILURE: No output found for {pdf.name}")
                
        except Exception as e:
            print(f"  > EXCEPTION processing {pdf.name}: {e}")
            import traceback
            traceback.print_exc()


def test_atomic_save_trigger():
    print("\n--- Testing Atomic Save (Move) Trigger ---")
    
    events_triggered = []
    def callback(path):
        print(f"CALLBACK TRIGGERED for: {path}")
        events_triggered.append(path)
    
    import tempfile
    import shutil
    
    tmp_dir = Path(tempfile.mkdtemp())
    print(f"Watching temp dir: {tmp_dir}")
    
    watcher = SystemWatcher(str(tmp_dir), callback)
    watcher.start()
    
    try:
        # Atomic Save Simulation
        # 1. Write to temp file
        temp_file = tmp_dir / "temp_123.tmp"
        target_file = tmp_dir / "atomic_save.pdf"
        
        print("Writing to temp file...")
        with open(temp_file, "w") as f:
            f.write("content")
            
        time.sleep(1)
        
        # 2. Rename/Move to target PDF
        print(f"Moving {temp_file.name} -> {target_file.name}")
        shutil.move(str(temp_file), str(target_file))
        
        # Wait for debounce
        print("Waiting for debounce...")
        time.sleep(3)
        
        if any("atomic_save.pdf" in str(e) for e in events_triggered):
            print("SUCCESS: Atomic save detected.")
        else:
            print("FAILURE: Atomic save NOT detected.")
        
    finally:
        watcher.stop()
        shutil.rmtree(tmp_dir)

if __name__ == "__main__":
    # test_full_pipeline() 
    # test_existing_files()
    test_atomic_save_trigger()
