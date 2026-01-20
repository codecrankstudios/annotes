import os
import yaml
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
import uvicorn
import webbrowser
import threading
import asyncio

# Import project modules
import settings
import annotes
import markdown

# --- Path Setup ---
# Initialize settings to ensure USER_DATA_DIR is available
settings.initialize()

# Config & Data live in User Data Dir (Persistent)
CONFIG_PATH = settings.USER_DATA_DIR / "config.yaml"
LOG_PATH = settings.USER_DATA_DIR / "app.log"

# Static Assets live in Resource Path (Bundled)
TEMPLATES_DIR = settings.get_resource_path("templates")
DOCS_PATH = settings.get_resource_path("settings_docs.yaml")
MANUAL_PATH = settings.get_resource_path("USER_MANUAL.md")
LOGO_PATH = settings.get_resource_path("app_icon.png")

app = FastAPI(title="Annotes | Pro Dashboard")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# --- Simple Caching ---
STATS_CACHE = {
    "data": None,
    "last_fetched": 0
}
CACHE_TTL = 10  # seconds

# --- Pydantic Models ---
class OutputSettings(BaseModel):
    annotated_file_tags: List[str] = Field(default_factory=list)

class AppSettings(BaseModel):
    pdf_folder: str
    notes_folder: str
    
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
    if LOGO_PATH.exists():
        return FileResponse(LOGO_PATH, media_type="image/png")
    return JSONResponse({"error": "Logo not found"}, status_code=404)

@app.get("/", response_class=HTMLResponse)
@app.get("/settings", response_class=HTMLResponse)
async def root(request: Request):
    """Dashboard Settings Page."""
    settings.initialize()
    config = settings.CONFIG
    docs = load_yaml(DOCS_PATH)
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "config": config,
        "docs": docs
    })

@app.get("/stats")
async def get_stats():
    settings.initialize()
    
    pdf_folder = Path(settings.CONFIG.get("pdf_folder", "."))
    notes_folder = Path(settings.CONFIG.get("notes_folder", "."))
    
    stats = {
        "pdfs": 0,
        "notes": 0,
        "syncs": 0,
        "errors": 0,
    }
    
    try:
        if pdf_folder.exists():
            stats["pdfs"] = len(list(pdf_folder.glob("*.pdf")))
    except: pass
        
    try:
        if notes_folder.exists():
            stats["notes"] = len(list(notes_folder.glob("*.md")))
    except: pass
        
    recent_logs = annotes.get_recent_logs()
    stats["recent_logs"] = recent_logs
    stats["syncs"] = sum(1 for line in recent_logs if "Synced:" in line)
    stats["errors"] = sum(1 for line in recent_logs if "ERROR" in line or "Exception" in line)
            
    return JSONResponse(content=stats)

@app.get("/events")
async def sse_endpoint(request: Request):
    """Server-Sent Events for real-time log streaming."""
    async def event_generator():
        yield f"data: Connected to log stream\n\n"
        last_index = len(annotes.LOG_BUFFER)
        
        while True:
            if await request.is_disconnected():
                break
            current_buffer = list(annotes.LOG_BUFFER)
            if len(current_buffer) > last_index:
                new_logs = current_buffer[last_index:]
                for log in new_logs:
                    clean_log = log.replace("\n", " ")
                    yield f"data: {clean_log}\n\n"
                last_index = len(current_buffer)
            if len(current_buffer) < last_index:
                last_index = 0
            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    html_content = ""
    if MANUAL_PATH.exists():
        with open(MANUAL_PATH, "r", encoding="utf-8") as f:
            text = f.read()
            html_body = markdown.markdown(text, extensions=['tables', 'fenced_code'])
            html_content = html_body
    else:
        html_content = "<h1>Usage Manual Not Found</h1><p>Ensure USER_MANUAL.md is bundled correctly.</p>"
    return templates.TemplateResponse("help.html", {"request": request, "content": html_content})

@app.get("/export-logs")
async def export_logs():
    if LOG_PATH.exists():
        return FileResponse(
            path=LOG_PATH,
            filename=f"annotes_debug_{int(time.time())}.log",
            media_type="text/plain"
        )
    return JSONResponse({"error": "Log file not found"}, status_code=404)

@app.post("/save")
async def save_settings(request: Request):
    form_data = await request.form()
    current_config = load_yaml(CONFIG_PATH)
    new_config = dict(current_config)
    
    for key, value in form_data.items():
        parts = key.split(".")
        ptr = new_config
        try:
            for part in parts[:-1]:
                if part not in ptr or not isinstance(ptr[part], dict):
                    ptr[part] = {}
                ptr = ptr[part]
            
            field = parts[-1]
            orig_val = ptr.get(field)
            
            if value == "" and orig_val is not None and not isinstance(orig_val, (str, list)):
                continue 
                
            if isinstance(orig_val, bool):
                ptr[field] = (str(value).lower() in ['true', 'on', '1', 'yes'])
            elif isinstance(orig_val, int):
                try: ptr[field] = int(value)
                except: pass
            elif isinstance(orig_val, list):
                if isinstance(value, str):
                    ptr[field] = [item.strip() for item in value.split(",") if item.strip()]
            else:
                ptr[field] = value
                
        except Exception as e:
            logging.error(f"Config Injection Error for {key}: {e}")

    try:
        AppSettings(
            pdf_folder=new_config.get("pdf_folder", ""),
            notes_folder=new_config.get("notes_folder", "")
        )
    except ValidationError as e:
        return JSONResponse({"status": "error", "message": f"Validation Error: {str(e)}"}, status_code=400)

    save_yaml(CONFIG_PATH, new_config)
    settings.initialize()
    
    return JSONResponse({"status": "success", "message": "Configuration synchronized successfully."})

class Server(uvicorn.Server):
    def install_signal_handlers(self):
        pass

def run_server(port: int = 8080):
    config = uvicorn.Config(
        app=app, 
        host="127.0.0.1", 
        port=port, 
        log_level="warning",
        reload=False
    )
    server = Server(config=config)
    server.run()

def open_dashboard(port: int = 8080):
    webbrowser.open(f"http://127.0.0.1:{port}")

if __name__ == "__main__":
    run_server()
