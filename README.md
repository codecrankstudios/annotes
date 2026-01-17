<div align="center">
  <img src="src/logo.png" width="128" height="128" alt="Annotes Logo">
  <h1>Annotes</h1>
  <p><strong>Extract Highlights from PDFs into Obsidian-Ready Markdown Notes</strong></p>
</div>

**Annotes** is a lightweight PDF annotation extractor designed for anyone who reads and highlights PDFs. Extract your highlights and comments directly into clean Markdown notes—ready to import into Obsidian for better organization and learning.

## ✨ Features

### 🎯 Smart Annotation Extraction
- **Intelligent Highlight Recognition**: Automatically extracts highlights and underlines from PDFs
- **Comment Preservation**: Captures author comments and notes attached to highlights
- **A2O-Style Formatting**: Hierarchical indent/join/append formatting for clean, readable notes
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

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/annotes.git
cd annotes/src

# Run with uv (auto-installs dependencies)
uv run tray_app.py
```

### Usage

1.  **Launch**: Run `uv run tray_app.py`.
2.  **System Tray**: Look for the **blue "A" icon** in your system tray.
3.  **Dashboard**: Double-click the tray icon to open the **Web Dashboard**.
4.  **Configure**: Set your `PDF Watch Folder` and `Markdown Output Folder` in the Dashboard.
5.  **Go**: Drop a PDF into your watch folder. It will be auto-processed!

---

## 📦 Building for Release

To build a standalone executable (no Python required for end-users), see [RELEASE_GUIDE.md](RELEASE_GUIDE.md).

---

## 🤝 Contributing

Annotes is built with:
- **FastAPI + Uvicorn**: Web Dashboard backend
- **PyMuPDF (fitz)**: PDF parsing
- **pystray**: System tray integration
- **Watchdog**: File system monitoring

To extend:
1.  Edit `src/config.yaml` for new defaults.
2.  Modify `src/formatter.py` for custom output styles.
3.  Debug logs are available in the Dashboard or `src/app.log`.

---

## 📄 License

MIT License. Free to use and modify.

**Made with ❤️ for knowledge workers, researchers, and note-takers.**
