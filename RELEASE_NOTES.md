# Release v1.0.2 (Stability & Setup)

This release focuses on improving the "out-of-the-box" experience by automating initial directory setup and path resolution.

## ✨ Improvements
- **Automatic Folder Creation**: Resolves "Invalid PDF folder" error on first run by automatically creating `PDFs` and `Notes` directories if they are missing.
- **Home Directory Support**: You can now use `~` in folder paths (e.g., `~/Documents/PDFs`).
- **Initialization Command**: Added `--init` flag to binaries to explicitly set up the config directory and base folders.

## 🐛 Bug Fixes
- **Cross-Platform Stability**: Ensured folder creation and path expansion work consistently across Windows, macOS, and Linux.

## 📦 Upgrading
- **Linux/macOS/Windows**: Download the new binary from this release.
- **Note**: If you already have `~/.annotes/config.yaml`, your existing settings will be preserved.

---

# Release v1.0.1 (Hotfix)

This is a critical hotfix for v1.0.0 that resolves a crash on startup for standalone binary releases (Linux, Windows, macOS).

## 🐛 Bug Fixes
- **Fixed Crash on Startup**: Resolved `Configuration file not found` error by implementing robust path resolution for persistent configuration.
- **Improved Persistence**: Configuration (`config.yaml`) and logs (`app.log`) are now stored in the user's home directory (`~/.annotes`) instead of the temporary execution folder.
- **Fixed Asset Loading**: The web dashboard now correctly loads templates and icons from within the bundled executable.

## 📦 Upgrading
- **Linux/macOS/Windows**: Download the new binary from this release.
- **Note**: This update will generate a new `config.yaml` in your user folder (`~/.annotes`). If you had previous settings, you may need to re-apply them via the dashboard.

---

# Release v1.0.0 (Original)


(See previous release notes for feature details)
