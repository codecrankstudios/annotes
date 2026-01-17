# 📘 Annotes User Manual

Welcome to **Annotes**, your tool for bridging the gap between PDF reading and Markdown note-taking. This guide will help you understand every feature and how to use the application effectively.

---

## 🚀 Getting Started

### 1. Installation
1.  **Download**: Get the latest release for your operating system (contact your administrator if you don't have the link).
2.  **Run**: Double-click the `Annotes` application.
3.  **System Tray**: You will see an **"A" icon** appear in your system tray (near the clock). The app is now running quietly in the background.

### 2. First-Time Setup
1.  **Open Dashboard**: Double-click the tray icon (or right-click and select **Docs & Web Settings**).
2.  **Configure Folders**:
    - **PDF Watch Folder**: Browse/Paste the path to the folder where you keep your PDFs (e.g., `~/Documents/Papers`).
    - **Markdown Export Folder**: Browse/Paste the path where you want your notes to appear (e.g., `~/Obsidian/Inbox`).
3.  **Save**: Click **Save Changes**.

---

## 🎯 Core Features & Usage

### 1. Automatic Extraction
**How it works**: Annotes watches your "PDF Watch Folder".
- **Step 1**: Open a PDF in your favorite reader (Adobe, Foxit, Preview, etc.).
- **Step 2**: Highlight text, underline key phrases, or add comments.
- **Step 3**: Save the PDF.
- **Step 4**: **That's it!** Annotes detects the change and automatically creates a Markdown note in your "Export Folder".

### 2. The Dashboard (`http://localhost:8080`)
Your command center for controlling Annotes.

#### **📊 Dashboard Tab**
- **Stats Cards**: See at a glance how many PDFs and Notes you have.
- **System Status**: confirms the engine is active.
- **Recent Activity**: A real-time log stream showing you exactly what the app is doing (e.g., *"Synced: Biology_101.pdf"*).

#### **⚙️ System Tab**
- **Settings**: Adjust global application behaviors and output paths.

### 3. Smart Formatting (The "A2O" System)
Annotes doesn't just dump text; it structures it. You can control the structure using **Symbols** in your PDF comments.

| Symbol | Action | Example Comment | Result |
| :--- | :--- | :--- | :--- |
| **`-`** | **Bullet Point** | `- This is a point` | `• [Highlighted Text]` |
| **`+`** | **Join Previous** | `+` | Merges highlight with the previous one. |
| **`/`** | **Append Text** | `/ Additional thought` | Adds text to the end of the highlight line. |
| **`>`** | **Blockquote** | `>` | Formats highlight as a Markdown blockquote. |
| **`#`** | **Heading** | `#` or `.h1` | Turns highlight into a Header. |

> **Pro Tip**: You can customize these symbols in the **Power Symbols** tab of the Dashboard.

### 4. Search & Linking
- **Page Links**: Every extracted highlight includes a link back to the exact page in the PDF.
    - *Example*: `(Page 5)` or `[[MyDoc.pdf#page=5]]`.
- **Obsidian Integration**: If you use Obsidian, enable **Wikilinks** in the **Smart Linking** tab for seamless navigation.

---

## 🧩 Advanced Features

### Metadata (YAML Frontmatter)
Perfect for Dataview users in Obsidian.
- Go to **Note Blueprint** > **Metadata Blocks**.
- Enable **Generate YAML Front Matter**.
- Customize keys: `title`, `author`, `tags`, `date_created`.

### Manual Scanning
If you dropped a bunch of files while the app was closed:
1.  Right-click the **Tray Icon**.
2.  Select **🔍 Scan Now**.
3.  The app will process all pending files immediately.

### Exporting Logs
Need to report a bug?
1.  Go to the **Raw Logs** tab in the Dashboard.
2.  Click **📥 Export Logs**.
3.  Send the file to support.

---

## 🔮 Future Roadmap
We are constantly improving Annotes. Here are features planned for upcoming releases:
- **Audio Feedback**: Optional sound effects for sync events.
- **Advanced Notifications**: Granular control over desktop alerts.
- **Deep Debugging**: Enhanced system logs for troubleshooting.
- **OCR Support**: Support for scanned image PDFs.

---

## ❓ FAQ

**Q: I saved my PDF but no note appeared?**
*A: Check the "Recent Activity" log in the Dashboard. The file might be skipped if no annotations were found, or if it hasn't changed since the last scan.*

**Q: Can I process scanned images?**
*A: Currently, Annotes focuses on text layers. For scanned images, run OCR on your PDF first.*

**Q: Where is the config file?**
*A: Settings are stored in `src/config.yaml` relative to the application, but you should always use the Dashboard to edit them.*

---

**Happy Reading!** 📚
