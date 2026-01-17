from abc import ABC, abstractmethod
from typing import List, Optional
import os
import logging
import sys

# Try to import pyperclip for clipboard support
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

class NoteConnector(ABC):
    """Abstract base class for note output connectors."""
    
    @abstractmethod
    def push_note(self, title: str, content: str, output_path: Optional[str] = None):
        """
        Push the note content to the destination.
        
        Args:
            title (str): Title of the note.
            content (str): The full markdown content of the note.
            output_path (str, optional): The suggested path for file-based connectors.
        """
        pass

class FileConnector(NoteConnector):
    """Writes notes to a file on the local filesystem."""
    
    def push_note(self, title: str, content: str, output_path: Optional[str] = None):
        if not output_path:
            logging.error("FileConnector requires an output_path")
            return

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            logging.info(f"Note saved to file: {output_path}")
        except Exception as e:
            logging.exception(f"Failed to save note to file: {e}")

class ClipboardConnector(NoteConnector):
    """Copies the note content to the system clipboard."""
    
    def push_note(self, title: str, content: str, output_path: Optional[str] = None):
        if not HAS_PYPERCLIP:
            logging.warning("pyperclip not installed. Cannot copy to clipboard.")
            return

        try:
            pyperclip.copy(content)
            logging.info(f"Note '{title}' copied to clipboard.")
        except Exception as e:
            logging.exception(f"Failed to copy note to clipboard: {e}")

class LogConnector(NoteConnector):
    """Prints the note content to the console/log."""
    
    def push_note(self, title: str, content: str, output_path: Optional[str] = None):
        print("="*40)
        print(f"NOTE: {title}")
        print("-" * 40)
        print(content)
        print("="*40)
        logging.info(f"Note '{title}' printed to log.")

class ConnectorFactory:
    """Factory to get connectors based on configuration."""
    
    @staticmethod
    def get_connectors(config: dict) -> List[NoteConnector]:
        connectors = []
        # Default behavior matches "File" output
        # In a real app, this would be parsed from config['connectors'] list
        # For now, we assume FileConnector is always active if output_path is provided
        connectors.append(FileConnector())
        
        # Check if clipboard is enabled in config (hypothetically)
        if config.get("output_settings", {}).get("copy_to_clipboard", False):
            connectors.append(ClipboardConnector())
            
        # Debug/Log connector
        if config.get("debug_mode", False):
            connectors.append(LogConnector())
            
        return connectors
