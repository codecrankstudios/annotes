<div align="center">
  <img src="src/logo.png" width="256" height="256" alt="Annotes Logo">
  <h1>Annotes</h1>
  <p><strong>Extract Highlights from PDFs into Obsidian-Ready Markdown Notes</strong></p>
</div>

**Annotes** is a lightweight PDF annotation extractor designed for anyone who reads and highlights PDFs. Extract your highlights and comments directly into clean Markdown notes—ready to import into Obsidian for better organization and learning.

## ✨ Features

### 🎯 Smart Annotation Extraction
- **Intelligent Highlight Recognition**: Automatically extracts highlights and underlines from PDFs
- **Comment Preservation**: Captures author comments and notes attached to highlights
- **Hierarchical Formatting**: Uses smart indentation and joining for clean, structured notes
- **Page References**: Optionally includes page links for quick navigation back to source

### 📊 Modern Web Dashboard
- **Web-Based Settings**: Configure everything via a beautiful local web interface (`http://localhost:8080`)
- **Real-Time Logging**: Watch your files being processed instantly with Server-Sent Events (SSE) streaming.
- **Stats at a Glance**: Track PDF counts, notes generated, and sync status.

### ⚡ Efficiency & Automation
- **Background Watcher**: Monitors your PDF folder and auto-processes new files.
- **Skip Unmodified PDFs**: Automatic mtime-based caching—only re-processes PDFs when they've changed
- **Lightweight**: Minimal dependencies, optimized for performance.

### 🔧 Highly Configurable
- **Custom Output Symbols**: Define symbols for indented items (`-`), appends (`/`), and joining (`+`)
- **Metadata Blocks**: Auto-generate YAML frontmatter for Obsidian Dataview.
- **Smart Linking**: Choose between deep Wikilinks or standard Markdown links.

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **uv** (Recommended) or pip

### Installation & Usage

#### Windows
1.  **Download**: Get `annotes-windows.exe` from the [Latest Release](https://github.com/codecrankstudios/annotes/releases).
2.  **Run**: Double-click the executable.
3.  **Use**: 
    - Look for the **blue "A" icon** in your system tray.
    - Double-click the tray icon to open the **Web Dashboard** (`http://localhost:8080`).
    - Configure your folders and drop in PDFs!

#### macOS
1.  **Download**: Get `annotes-macos.zip` from the [Latest Release](https://github.com/codecrankstudios/annotes/releases).
2.  **Install**: Unzip the file and drag `Annotes.app` to your `Applications` folder.
3.  **Run**: Open `Annotes` from Applications.
    > **Note**: Since the app is not signed by Apple, you may need to right-click and select "Open", or go to System Settings > Privacy & Security to allow it to run the first time.

#### Linux
1.  **Download**: Get `annotes-linux` from the [Latest Release](https://github.com/codecrankstudios/annotes/releases).
2.  **Permissions**: Make the file executable:
    ```bash
    chmod +x annotes-linux
    ```
3.  **Run**:
    ```bash
    ./annotes-linux
    ```
    > **Tip**: On the first run, Annotes will automatically create a configuration directory at `~/.annotes` and default `PDFs` and `Notes` folders in your current directory. You can also run `./annotes-linux --init` to explicitly set up paths.


#### Running from Source (Developers)
If you prefer to run the raw Python code:
```bash
git clone https://github.com/codecrankstudios/annotes.git
cd annotes/src
uv run tray_app.py
```

## 📦 Building for Release

To build a standalone executable (no Python required for end-users), see [RELEASE_GUIDE.md](RELEASE_GUIDE.md).

---

## 🤝 Contributing

We welcome contributions to make Annotes better! 

### How you can help:
- **Report Bugs**: Found a PDF that doesn't parse correctly? Open an Issue!
- **Suggest Features**: Have an idea for better note formatting? Let us know.
- **Submit PRs**: 
    1.  Fork the repository.
    2.  Create a feature branch.
    3.  Make your changes (see `src/config.yaml` and `src/formatter.py`).
    4.  Submit a Pull Request.

**Core Tech Stack**:
- **FastAPI + Uvicorn**: Web Dashboard backend
- **PyMuPDF (fitz)**: PDF parsing
- **pystray**: System tray integration
- **Watchdog**: File system monitoring

---

## 📄 License

MIT License. Free to use and modify.

**Made with ❤️ for knowledge workers, researchers, and note-takers.**
