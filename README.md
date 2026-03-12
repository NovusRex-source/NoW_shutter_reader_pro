<p align="center">
  <img src="Icon/now_shuttercount.png" alt="Canon Shutter Counter Pro" width="100">
</p>

# Canon Shutter Counter Pro

Professional shutter count reader for Canon R-series cameras.

---

## Quick Start

**Run from source**
```bash
pip install -r requirements.txt
python CanonShutterCounter.py
```

**Or use the pre-built EXE** — `dist/CanonShutterCounter.exe`  
→ `exiftool.exe` must be in the same folder.

---

## Build EXE

```bash
pyinstaller --clean CanonShutterCounter.spec
```

Output: `dist/CanonShutterCounter.exe`  
Then copy `exiftool.exe` into `dist/`.

---

## Supported Cameras

Canon EOS R1, R3, R5, R5 II, R6, R6 II, R6 III, R8, RP

---

## Project Structure

```
CanonShutterCounter.py   # Main app & UI wiring
camera_metadata.py       # Backend: ExifTool, USB, metadata
ui_components.py         # UI: design system, widgets, tabs
requirements.txt         # Python dependencies
CanonShutterCounter.spec # PyInstaller build config
```

---

## Docs

- [Changelog](CHANGELOG.md)
- [License](LICENSE.txt)

---

**Author:** Noel Wangler – [noelwangler.ch](https://noelwangler.ch)
