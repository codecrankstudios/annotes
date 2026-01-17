import os
import yaml
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
import uvicorn
import webbrowser
import threading

# Import project modules
import settings
import annotes
import markdown # New dependency

# Path Setup
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.yaml"
DOCS_PATH = BASE_DIR / "settings_docs.yaml"

app = FastAPI(title="Annotes | Pro Dashboard")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# --- Simple Caching ---
STATS_CACHE = {
    "data": None,
    "last_fetched": 0
}
CACHE_TTL = 10  # seconds

# --- Pydantic Models ---
class OutputSettings(BaseModel):
    annotated_file_tags: List[str] = Field(default_factory=list)
    # can add more recursive models here as needed

class AppSettings(BaseModel):
    """
    Validates key configuration fields. 
    Note: Dynamic/nested dicts from the frontend form are harder to map 1:1 
    without a complex nested model, so we do specific field validation.
    """
    pdf_folder: str
    notes_folder: str
    
    # Allow extra fields for now since the config is flexible
    class Config:
        extra = "allow" 

def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}

def save_yaml(path: Path, data: Dict[str, Any]):
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)

@app.get("/logo.png")
async def get_logo():
    # Serve the new icon file
    logo_path = BASE_DIR / "app_icon.png"
    if logo_path.exists():
        return FileResponse(logo_path, media_type="image/png")
    return JSONResponse({"error": "Logo not found"}, status_code=404)

@app.get("/", response_class=HTMLResponse)
@app.get("/settings", response_class=HTMLResponse)
async def root(request: Request):
    """Dashboard Settings Page."""
    # Ensure settings are loaded from disk to be fresh
    settings.initialize()
    config = settings.CONFIG
    docs = load_yaml(DOCS_PATH)
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "config": config,
        "docs": docs
    })

from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
import time
import asyncio

# ... (Imports remain the same) ...

@app.get("/stats")
async def get_stats():
    # Refresh config for stats logic
    settings.initialize()
    
    pdf_folder = Path(settings.CONFIG.get("pdf_folder", "."))
    notes_folder = Path(settings.CONFIG.get("notes_folder", "."))
    
    stats = {
        "pdfs": 0,
        "notes": 0,
        "syncs": 0, # Calculated from memory logs for now, or could persist count
        "errors": 0,
    }
    
    # 1. Count PDFs
    try:
        if pdf_folder.exists():
            stats["pdfs"] = len(list(pdf_folder.glob("*.pdf")))
    except: pass
        
    # 2. Count Notes
    try:
        if notes_folder.exists():
            stats["notes"] = len(list(notes_folder.glob("*.md")))
    except: pass
        
    # 3. Memory Logs
    # We don't read disk anymore for recent logs to save I/O
    # Stats like total syncs/errors are harder to count without persistence, 
    # so we'll just count what's in the buffer for "Recent Activity" context.
    
    recent_logs = annotes.get_recent_logs()
    stats["recent_logs"] = recent_logs
    stats["syncs"] = sum(1 for line in recent_logs if "Synced:" in line)
    stats["errors"] = sum(1 for line in recent_logs if "ERROR" in line or "Exception" in line)
            
    return JSONResponse(content=stats)

@app.get("/events")
async def sse_endpoint(request: Request):
    """Server-Sent Events for real-time log streaming."""
    async def event_generator():
        # Yield connection confirmation
        yield f"data: Connected to log stream\n\n"
        
        last_index = len(annotes.LOG_BUFFER)
        
        while True:
            if await request.is_disconnected():
                break
                
            current_buffer = list(annotes.LOG_BUFFER)
            if len(current_buffer) > last_index:
                # New logs arrived
                new_logs = current_buffer[last_index:]
                for log in new_logs:
                    # Clean newlines for SSE format
                    clean_log = log.replace("\n", " ")
                    yield f"data: {clean_log}\n\n"
                last_index = len(current_buffer)
            
            # Reset index if buffer rotated (shrunk effectively or wrapped)
            if len(current_buffer) < last_index:
                last_index = 0
                
            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    """Serves USER_MANUAL.md as HTML."""
    manual_path = BASE_DIR.parent / "USER_MANUAL.md"
    html_content = ""
    
    if manual_path.exists():
        with open(manual_path, "r", encoding="utf-8") as f:
            text = f.read()
            # Convert Markdown to HTML
            html_body = markdown.markdown(text, extensions=['tables', 'fenced_code'])
            html_content = html_body
    else:
        html_content = "<h1>Usage Manual Not Found</h1><p>Ensure USER_MANUAL.md exists in the root directory.</p>"
        
    return templates.TemplateResponse("help.html", {"request": request, "content": html_content})


@app.get("/export-logs")
async def export_logs():
    """Downloads the current app.log file."""
    log_path = Path(__file__).parent / "app.log"
    if log_path.exists():
        return FileResponse(
            path=log_path,
            filename=f"annotes_debug_{int(time.time())}.log",
            media_type="text/plain"
        )
    return JSONResponse({"error": "Log file not found"}, status_code=404)

@app.post("/save")
async def save_settings(request: Request):
    form_data = await request.form()
    
    # Start with a fresh reload of the current config
    current_config = load_yaml(CONFIG_PATH)
    
    new_config = dict(current_config)
    
    # Temporary dict to build flat key-values into nested struct for Pydantic validation if we wanted full schema
    # For now, we will just injection-protect and basic-validate.
    
    for key, value in form_data.items():
        parts = key.split(".")
        ptr = new_config
        
        try:
            # Traversal
            for part in parts[:-1]:
                if part not in ptr or not isinstance(ptr[part], dict):
                    ptr[part] = {}
                ptr = ptr[part]
            
            field = parts[-1]
            # Smart Type Detection & Conversion
            # We look at the EXISTING value to determine type
            orig_val = ptr.get(field)
            
            # Handle empty strings as None/Empty depending on type
            if value == "" and orig_val is not None and not isinstance(orig_val, (str, list)):
                continue # Skip setting non-string fields to empty
                
            if isinstance(orig_val, bool):
                ptr[field] = (str(value).lower() in ['true', 'on', '1', 'yes'])
            elif isinstance(orig_val, int):
                try: ptr[field] = int(value)
                except: pass
            elif isinstance(orig_val, list):
                # Comma separated list from form
                if isinstance(value, str):
                    ptr[field] = [item.strip() for item in value.split(",") if item.strip()]
            else:
                # Default to string
                ptr[field] = value
                
        except Exception as e:
            logging.error(f"Config Injection Error for {key}: {e}")

    # Validate critical fields with Pydantic
    try:
        # We only strictly validate the top-level paths for now to prevent corruption
        AppSettings(
            pdf_folder=new_config.get("pdf_folder", ""),
            notes_folder=new_config.get("notes_folder", "")
        )
    except ValidationError as e:
        return JSONResponse({
            "status": "error",
            "message": f"Validation Error: {str(e)}"
        }, status_code=400)

    # Write back to disk
    save_yaml(CONFIG_PATH, new_config)
    
    # Reload global settings in memory
    settings.initialize()
    
    return JSONResponse({
        "status": "success", 
        "message": "Configuration synchronized successfully."
    })

class Server(uvicorn.Server):
    def install_signal_handlers(self):
        # Override to prevent secondary threads from hijacking Ctrl+C
        pass

def run_server(port: int = 8080):
    config = uvicorn.Config(
        app=app, 
        host="127.0.0.1", 
        port=port, 
        log_level="warning", # Quieter console
        reload=False
    )
    server = Server(config=config)
    server.run()

def open_dashboard(port: int = 8080):
    webbrowser.open(f"http://127.0.0.1:{port}")

if __name__ == "__main__":
    run_server()
