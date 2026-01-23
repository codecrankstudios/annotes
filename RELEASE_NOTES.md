# Release v1.0.3 (Tray & UI Polish)

This release addresses issues with system tray icons and interactions, particularly on Linux.

## ✨ Improvements
- **Optimized Tray Icons**: Icons are now automatically resized and converted to RGBA mode, fixing "solid block" rendering issues on many Linux desktop environments and Windows.
- **Enhanced Reliability**: Improved error handling during icon loading and added a high-visibility fallback icon.
- **Better UX**: Double-clicking the tray icon now correctly opens the Web Dashboard.
- **Improved Logging**: Added detailed startup and runtime logging to help diagnose tray backend issues.

## 🐛 Bug Fixes
- **Linux Interactivity**: Fixed issues where right-clicking the tray icon would not open the menu in certain environments.
- **Scaling Fixes**: Resolved issues where high-resolution icons caused the tray area to misbehave.

## 📦 Upgrading
- **Linux/macOS/Windows**: Download the new binary from this release.

---

# Release v1.0.2 (Stability & Setup)

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
