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
