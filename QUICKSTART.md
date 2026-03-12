# 🚀 Quick Start Guide

## For End Users (Non-Programmers)

### Download & Run
1. Download the latest release from [Releases](https://github.com/YourUsername/canon-shutter-counter/releases)
2. Extract the ZIP file
3. Double-click `CanonShutterCounter.exe`
4. Done! ✅

**Note:** Make sure `exiftool.exe` is in the same folder as the main executable.

---

## For Developers

### Setup Development Environment

```bash
# 1. Clone repository
git clone https://github.com/YourUsername/canon-shutter-counter.git
cd canon-shutter-counter

# 2. Install dependencies
pip install -r requirements.txt
# or run: setup.bat

# 3. Run application
python CanonShutterCounter.py
# or run: START_HERE.bat
```

### Build Standalone EXE

```bash
# Run the build script
build_simple.bat

# The EXE will be created in: dist\CanonShutterCounter.exe
```

### Create Distribution Package

```bash
# First build the EXE, then create distribution package
create_distribution.bat

# This creates a ready-to-distribute folder with all necessary files
```

---

## First Time Using the App?

### Option 1: File Reader (Recommended)
1. Click on the **"File"** tab
2. Click **"Browse File"** or drag & drop a CR3 file
3. Click **"Read Shutter Count"**
4. View the results!

### Option 2: USB Camera
1. Connect your Canon camera via USB
2. Click on the **"USB"** tab
3. Click **"Detect Camera"**
4. Click **"Read from Camera"** if detected

### Option 3: Batch Processing
1. Click on the **"Batch"** tab
2. Select a folder containing CR3 files
3. Click **"Start Batch Processing"**
4. Export results when done

---

## Toggle Dark/Light Mode

Click the **🌙 Dark Mode** / **☀️ Light Mode** button in the top-right corner.

---

## Troubleshooting

### "ExifTool not found"
- Make sure `exiftool.exe` is in the same folder as the main program
- Download from: https://exiftool.org/

### "No shutter count found"
- Canon R-series cameras typically don't store shutter count in CR3 files
- Try USB mode or use Canon EOS Utility for accurate readings

### "Camera not detected"
- Make sure camera is turned ON
- Try a different USB cable or port
- Install Canon camera drivers if needed

---

## Need Help?

- Check the **[README.md](README.md)** for full documentation
- Visit developer website: [noelwangler.ch](https://noelwangler.ch)
- Open an issue on GitHub

---

**Developer:** Noel Wangler - NoW Photography  
**License:** See LICENSE.txt

