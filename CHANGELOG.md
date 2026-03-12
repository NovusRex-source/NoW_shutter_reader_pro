# Changelog

## [2.0.0] - 2026-03-12

### Added
- Dark / light mode toggle
- Fully redesigned UI — custom design system, rounded buttons, responsive layout
- Modular architecture: `camera_metadata.py`, `ui_components.py`
- Real-time progress tracking for batch processing
- Standalone EXE build via PyInstaller

### Changed
- Migrated all UI to native `tk` widgets with custom `Theme` class
- Improved EXIF data formatting
- Cleaner code structure (separation of concerns)

### Fixed
- USB camera detection on Windows 11
- ExifTool path resolution
- Batch processing memory optimisation

---

## [1.0.0] - Legacy

- Basic CR3 file reading
- Simple USB camera detection
- Basic GUI interface
