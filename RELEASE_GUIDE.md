# 🚀 Annotes Release Guide

This guide explains how to package **Annotes** as a standalone executable and release it on GitHub/GitLab.

## 1. Prepare for Release

1.  **Version Bump**: Update the version number in `pyproject.toml` and `src/templates/settings.html` (if displayed).
2.  **Clean Up**: Ensure `src/app.log` and `src/annotes.lock` are not included or are ignored.
3.  **Test**: Run `test_release.py` one last time.

## 2. Build Standalone Executable (PyInstaller)

We use `pyinstaller` to bundle Python and all dependencies into a single file.

### Linux Build
```bash
cd src
uv run pyinstaller --noconfirm --onefile --windowed \
    --name "Annotes" \
    --add-data "templates:templates" \
    --add-data "settings_docs.yaml:." \
    --add-data "config.yaml:." \
    --hidden-import "uvicorn.loops.auto" \
    --hidden-import "uvicorn.protocols.http.auto" \
    --collect-all "pymupdf" \
    tray_app.py
```
*Output*: The executable will be in `src/dist/Annotes`.

### Windows Build (Run on Windows)
```powershell
uv run pyinstaller --noconfirm --onefile --windowed `
    --name "Annotes" `
    --add-data "templates;templates" `
    --add-data "settings_docs.yaml;." `
    --add-data "config.yaml;." `
    tray_app.py
```
*Note*: The separator for `--add-data` is `;` on Windows and `:` on Linux.

## 3. Create a GitHub/GitLab Release

1.  **Commit & Push**:
    ```bash
    git add .
    git commit -m "Release v1.0.0"
    git push origin main
    ```
2.  **Tag**:
    ```bash
    git tag v1.0.0
    git push origin v1.0.0
    ```
3.  **Draft Release**:
    - Go to your repository > **Releases** > **Draft a new release**.
    - Select tag `v1.0.0`.
    - Title: `Annotes v1.0.0`.
    - Description: Paste the "What's New" from `walkthrough.md`.
    - **Upload Binaries**: Drag and drop the `Annotes` (Linux) or `Annotes.exe` (Windows) file from `src/dist/`.
4.  **Publish**: Click "Publish release".

## 4. Hosting for Free

Since this is a free tool, GitHub/GitLab Releases is the best place to host binary downloads. Users can simply download the executable and run it without installing Python.
