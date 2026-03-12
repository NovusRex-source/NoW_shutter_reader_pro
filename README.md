# Canon Shutter Counter Pro

<p align="center">
  <img src="Icon/now_shuttercount.png" alt="Canon Shutter Counter Pro Logo" width="128">
</p>

<p align="center">
  <strong>Professional Shutter Count Reader for Canon R-Series Cameras</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#supported-cameras">Supported Cameras</a> •
  <a href="#building">Building</a> •
  <a href="#license">License</a>
</p>

---

## 📷 About

Canon Shutter Counter Pro is a modern, professional tool for reading shutter count and camera metadata from Canon R-series cameras. Developed by **Noel Wangler - NoW Photography** ([noelwangler.ch](https://noelwangler.ch)).

### Key Highlights

- ✨ **Modern UI** with dark/light mode toggle
- 📁 **File Reader** - Analyze CR3 RAW files
- 🔌 **USB Camera Detection** - Direct camera connection
- 📦 **Batch Processing** - Process entire folders
- 🎨 **Responsive Design** - Clean and intuitive interface
- 🚀 **Standalone EXE** - No Python installation required

---

## 🌟 Features

### 1. File Reader
- Drag & drop CR3 files or browse
- Extract comprehensive EXIF metadata
- Display shutter count (when available)
- Color-coded, formatted output

### 2. USB Camera Reader
- Automatic Canon camera detection via USB
- Live connection status
- Direct metadata reading from camera

### 3. Batch Processing
- Process entire folders of CR3 files
- Real-time progress tracking
- Export results to text file
- Professional summary statistics

### 4. Modern Interface
- **Dark Mode** and **Light Mode** with smooth toggle
- Responsive, scalable layout
- Professional card-based design
- Intuitive navigation with tabbed interface
- Real-time status updates

---

## 📋 Requirements

### For Python Version
- Python 3.8 or higher
- Windows OS (for USB camera detection)
- ExifTool (included in repository)

### Python Dependencies
```
ttkbootstrap>=1.10.1
pywin32>=305
```

---

## 🚀 Installation

### Option 1: Python Script (Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/YourUsername/canon-shutter-counter.git
   cd canon-shutter-counter
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or run the setup script:
   ```bash
   setup.bat
   ```

3. **Run the application**
   ```bash
   python CanonShutterCounter.py
   ```
   
   Or use the launcher:
   ```bash
   START_HERE.bat
   ```

### Option 2: Standalone EXE (End Users)

1. Download the latest release from [Releases](https://github.com/YourUsername/canon-shutter-counter/releases)
2. Extract the ZIP file
3. Run `CanonShutterCounter.exe`

**Note:** `exiftool.exe` must be in the same folder as the main executable.

---

## 📖 Usage

### Quick Start

1. **Launch the application**
   - Python: Run `START_HERE.bat` or `python CanonShutterCounter.py`
   - Standalone: Double-click `CanonShutterCounter.exe`

2. **Choose your method**
   - **File Tab**: Browse or drag CR3 files
   - **USB Tab**: Connect your Canon camera via USB
   - **Batch Tab**: Process entire folders

3. **Read the shutter count**
   - Click the appropriate "Read" button
   - View formatted results in the output area
   - Copy results or export to file

### Dark/Light Mode Toggle

Click the **🌙 Dark Mode** / **☀️ Light Mode** button in the top-right corner to switch themes.

---

## 📷 Supported Cameras

Canon EOS R-Series:
- EOS R1
- EOS R3
- EOS R5, R5 II
- EOS R6, R6 II, R6 III
- EOS R8
- EOS RP

> **Note:** Canon R-series cameras typically do not store shutter count in CR3 EXIF metadata. For accurate USB shutter count reading, official tools like Canon EOS Utility or EOSInfo are recommended.

---

## 🔨 Building

### Build Standalone EXE

Run the build script:
```bash
build_simple.bat
```

This will create a portable `.exe` file in the `dist` folder using PyInstaller.

### Build Configuration

The build process:
1. Packages all Python dependencies
2. Embeds the application icon
3. Includes ExifTool
4. Creates a single-file executable
5. No console window (GUI mode)

To customize the build, edit `CanonShutterCounter.spec` and run:
```bash
pyinstaller CanonShutterCounter.spec
```

---

## 📦 Project Structure

```
canon-shutter-counter/
├── CanonShutterCounter.py    # Main application
├── requirements.txt           # Python dependencies
├── setup.bat                  # Dependency installer
├── START_HERE.bat             # Application launcher
├── build_simple.bat           # Build script
├── exiftool.exe               # ExifTool binary
├── Icon/                      # Application icons
│   ├── now_shuttercount.ico
│   └── now_shuttercount.png
├── exiftool_files/            # ExifTool supporting files
├── LICENSE.txt                # Software license
├── CREDITS.txt                # Third-party attributions
└── README.md                  # This file
```

---

## 🙏 Credits

This software uses the following open-source components:

- **[ExifTool](https://exiftool.org/)** by Phil Harvey - Metadata extraction
- **[Python](https://www.python.org/)** by Python Software Foundation - Core runtime
- **[ttkbootstrap](https://ttkbootstrap.readthedocs.io/)** by Israel Dryer - Modern UI framework
- **[PyWin32](https://github.com/mhammond/pywin32)** by Mark Hammond - Windows COM interface
- **[Tkinter](https://docs.python.org/3/library/tkinter.html)** - GUI framework
- **[PyInstaller](https://pyinstaller.org/)** - Executable packaging

See [CREDITS.txt](CREDITS.txt) for detailed attribution.

---

## 📄 License

Copyright (c) 2026 **Noel Wangler - NoW Photography**  
Website: [noelwangler.ch](https://noelwangler.ch)

This software is provided "as is" without warranty of any kind. See [LICENSE.txt](LICENSE.txt) for full terms.

**Disclaimer:** This software is not affiliated with or endorsed by Canon Inc. Canon and EOS are registered trademarks of Canon Inc.

---

## 🌐 Contact

**Developer:** Noel Wangler - NoW Photography  
**Website:** [noelwangler.ch](https://noelwangler.ch)

For questions, suggestions, or support, please visit the website or open an issue on GitHub.

---

<p align="center">
  Made with ❤️ for the photography community
</p>

