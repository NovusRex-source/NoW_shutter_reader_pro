#!/usr/bin/env python3
"""
Camera Metadata Module
Handles all camera metadata extraction and processing logic
"""

import subprocess
import os
import sys
import shutil
from pathlib import Path
import platform

try:
    import win32com.client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False


class CameraMetadataReader:
    """Handles reading camera metadata from files and USB devices"""

    def __init__(self):
        self.exiftool_path = self.find_exiftool()

    def find_exiftool(self):
        """
        Find ExifTool executable.
        When running as a PyInstaller bundle, exiftool.exe is embedded as a
        binary resource and extracted to a persistent temp directory on first
        call so it can be executed by subprocess.
        """
        # 1. Running frozen (PyInstaller onefile) – extract from bundle
        if getattr(sys, 'frozen', False):
            bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            src = os.path.join(bundle_dir, "exiftool.exe")
            if os.path.exists(src):
                # Copy to a writable temp location (MEIPASS may be read-only)
                import tempfile
                dest_dir = os.path.join(tempfile.gettempdir(), "CanonShutterCounter")
                os.makedirs(dest_dir, exist_ok=True)
                dest = os.path.join(dest_dir, "exiftool.exe")
                if not os.path.exists(dest):
                    shutil.copy2(src, dest)
                return dest

        # 2. Development / unfrozen – look next to the script or on PATH
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for candidate in [
            os.path.join(script_dir, "exiftool.exe"),
            os.path.join(script_dir, "exiftool"),
            "exiftool.exe",
            "exiftool",
        ]:
            if os.path.exists(candidate):
                return candidate

        return shutil.which("exiftool")

    @staticmethod
    def get_camera_shutter_rating(model):
        """Get expected shutter rating for camera model"""
        if not model:
            return 200000

        model_upper = model.upper()

        if any(x in model_upper for x in ['R1', 'R3']):
            return 500000
        if any(x in model_upper for x in ['R5', 'R6 II', 'R6 III']):
            return 500000

        return 200000

    def get_camera_metadata(self, image_path):
        """Extract metadata from a camera RAW file"""
        metadata = {
            "shutter_count": None,
            "image_number": None,
            "file_number": None,
            "serial_number": None,
            "camera_model": None,
            "shutter_rating": None,
            "error": None
        }

        if not self.exiftool_path:
            metadata["error"] = "ExifTool not found. Install from https://exiftool.org/"
            return metadata

        if not os.path.exists(image_path):
            metadata["error"] = f"File not found: {image_path}"
            return metadata

        command = [
            self.exiftool_path,
            "-ShutterCount", "-ShutterCounter", "-ImageCount", "-ImageNumber",
            "-FileNumber", "-InternalSerialNumber", "-Model", "-SerialNumber",
            "-s", image_path
        ]

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            if result.returncode != 0:
                metadata["error"] = f"ExifTool error: {result.stderr.strip()}"
                return metadata

            for line in result.stdout.split("\n"):
                line = line.strip()
                if not line or ":" not in line:
                    continue

                key, value = line.split(":", 1)
                key, value = key.strip(), value.strip()

                if key in ["ShutterCount", "ShutterCounter", "ImageCount"]:
                    metadata["shutter_count"] = value
                elif key == "ImageNumber":
                    if not metadata["shutter_count"]:
                        metadata["shutter_count"] = value
                    metadata["image_number"] = value
                elif key == "FileNumber":
                    metadata["file_number"] = value
                elif key in ["InternalSerialNumber", "SerialNumber"]:
                    if not metadata["serial_number"]:
                        metadata["serial_number"] = value
                elif key == "Model":
                    metadata["camera_model"] = value

            if metadata["camera_model"]:
                metadata["shutter_rating"] = self.get_camera_shutter_rating(
                    metadata["camera_model"]
                )

            if metadata["shutter_count"] is None:
                if metadata["camera_model"] and any(
                    x in metadata["camera_model"].upper()
                    for x in ['R5', 'R6', 'R3', 'R1', 'R8', 'RP']
                ):
                    metadata["error"] = (
                        f"Shutter count not in EXIF for {metadata['camera_model']}. "
                        "Use EOSInfo or Canon EOS Utility."
                    )
                else:
                    metadata["error"] = "Shutter count not found in file."

        except subprocess.TimeoutExpired:
            metadata["error"] = "ExifTool timed out"
        except Exception as e:
            metadata["error"] = f"Error: {str(e)}"

        return metadata

    @staticmethod
    def format_metadata_output(filename, metadata):
        """Format metadata as a nice text output"""
        lines = [f"╔{'═' * 58}╗"]
        lines.append(f"║ FILE: {filename[:51]:<51}║")
        lines.append(f"╠{'═' * 58}╣")

        if metadata.get("camera_model"):
            lines.append(f"║ Camera:    {metadata['camera_model']:<45}║")

        if metadata.get("serial_number"):
            lines.append(f"║ Serial:    {metadata['serial_number']:<45}║")

        if metadata.get("shutter_count"):
            try:
                count = int(metadata["shutter_count"])
                lines.append(
                    f"║ Shutter:   {count:,} actuations"
                    f"{' ' * (34 - len(str(count)))}║"
                )

                rating = metadata.get("shutter_rating", 200000)
                wear = (count / rating) * 100
                bar_length = 30
                filled = int((wear / 100) * bar_length)
                bar = "█" * filled + "░" * (bar_length - filled)
                lines.append(f"║ Wear:      {wear:5.1f}% [{bar}] ║")
                lines.append(
                    f"║            (rated for {rating:,} actuations)"
                    f"{' ' * (24 - len(str(rating)))}║"
                )
            except (ValueError, TypeError):
                lines.append(f"║ Shutter:   {metadata['shutter_count']:<45}║")

        if metadata.get("file_number"):
            lines.append(f"║ File #:    {metadata['file_number']:<45}║")

        if metadata.get("error"):
            lines.append(f"╠{'═' * 58}╣")
            error_lines = metadata['error'].split('. ')
            for error_line in error_lines:
                if error_line:
                    while len(error_line) > 50:
                        lines.append(f"║ WARNING: {error_line[:50]:<51}║")
                        error_line = error_line[50:]
                    if error_line:
                        lines.append(f"║ WARNING: {error_line:<51}║")

        lines.append(f"╚{'═' * 58}╝")
        return "\n".join(lines)

    def batch_process_folder(self, folder_path):
        """Process all CR3 files in a folder"""
        cr3_files = (
            list(Path(folder_path).glob("*.CR3")) +
            list(Path(folder_path).glob("*.cr3"))
        )
        return cr3_files

    def get_exiftool_version(self):
        """Get ExifTool version"""
        if not self.exiftool_path:
            return None

        try:
            result = subprocess.run(
                [self.exiftool_path, "-ver"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            return result.stdout.strip()
        except:
            return "Found"


class USBCameraDetector:
    """Handles USB camera detection and reading"""

    @staticmethod
    def detect_camera():
        """Detect connected camera via WIA"""
        result_lines = ["╔══════════════════════════════════════════════════════════╗"]
        result_lines.append("║           CAMERA DETECTION RESULTS                       ║")
        result_lines.append("╠══════════════════════════════════════════════════════════╣")

        if platform.system() == "Windows" and HAS_WIN32COM:
            result_lines.append("║ Method: Windows WIA                                      ║")
            try:
                device_manager = win32com.client.Dispatch("WIA.DeviceManager")
                found = False

                for i in range(1, device_manager.DeviceInfos.Count + 1):
                    device_info = device_manager.DeviceInfos.Item(i)
                    if device_info.Type == 2:
                        found = True
                        name = device_info.Properties('Name').Value
                        mfr = device_info.Properties('Manufacturer').Value
                        result_lines.append("╠══════════════════════════════════════════════════════════╣")
                        result_lines.append(f"║ [OK] Camera Found: {name[:42]:<42}║")
                        result_lines.append(f"║      Manufacturer: {mfr[:42]:<42}║")

                if not found:
                    result_lines.append("╠══════════════════════════════════════════════════════════╣")
                    result_lines.append("║ [FAIL] No camera detected via WIA                        ║")

            except Exception as e:
                result_lines.append("╠══════════════════════════════════════════════════════════╣")
                result_lines.append(f"║ [ERROR] WIA Error: {str(e)[:45]:<45}║")
        else:
            result_lines.append("╠══════════════════════════════════════════════════════════╣")
            result_lines.append("║ Windows WIA: Not available                               ║")

        result_lines.append("╠══════════════════════════════════════════════════════════╣")
        result_lines.append("║ NOTE: Most Canon R-series cameras require EOSInfo or     ║")
        result_lines.append("║       Canon EOS Utility for shutter count reading via USB. ║")
        result_lines.append("╚══════════════════════════════════════════════════════════╝")

        return "\n".join(result_lines)

    @staticmethod
    def read_usb_camera():
        """Read camera information via USB"""
        result_lines = ["╔══════════════════════════════════════════════════════════╗"]
        result_lines.append("║           USB CAMERA READING                             ║")
        result_lines.append("╠══════════════════════════════════════════════════════════╣")

        if platform.system() == "Windows" and HAS_WIN32COM:
            try:
                device_manager = win32com.client.Dispatch("WIA.DeviceManager")
                found = False

                for i in range(1, device_manager.DeviceInfos.Count + 1):
                    device_info = device_manager.DeviceInfos.Item(i)
                    if device_info.Type == 2:
                        found = True
                        name = device_info.Properties('Name').Value
                        result_lines.append(f"║ Camera: {name[:47]:<47}║")
                        result_lines.append("╠══════════════════════════════════════════════════════════╣")

                        device = device_info.Connect()
                        prop_count = 0
                        for j in range(1, device.Properties.Count + 1):
                            try:
                                prop = device.Properties.Item(j)
                                prop_name = prop.Name[:20]
                                prop_val = str(prop.Value)[:35]
                                result_lines.append(f"║ {prop_name:<20}: {prop_val:<35}║")
                                prop_count += 1
                            except:
                                pass

                        if prop_count == 0:
                            result_lines.append("║ No detailed properties available                         ║")

                if not found:
                    result_lines.append("║ [FAIL] No camera detected                                ║")
                    result_lines.append("╞══════════════════════════════════════════════════════════╡")
                    result_lines.append("║ TIP: Use EOSInfo for Canon R-series                     ║")

            except Exception as e:
                result_lines.append(f"║ [ERROR] Error: {str(e)[:49]:<49}║")
                result_lines.append("╠══════════════════════════════════════════════════════════╣")
                result_lines.append("║ Canon R-series cameras often restrict USB access to      ║")
                result_lines.append("║ shutter count. Use EOSInfo or Canon EOS Utility.         ║")
        else:
            result_lines.append("║ USB reading requires Windows with PyWin32                ║")
            result_lines.append("╠══════════════════════════════════════════════════════════╣")
            result_lines.append("║ TIP: Use EOSInfo (recommended)                           ║")

        result_lines.append("╚══════════════════════════════════════════════════════════╝")

        return "\n".join(result_lines)


class DependencyChecker:
    """Check system dependencies"""

    def __init__(self, exiftool_path=None):
        self.exiftool_path = exiftool_path

    def check_all(self):
        """Check all dependencies and return results"""
        deps = []

        # Python version
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        deps.append(("Python", py_version, True))

        # ExifTool
        if self.exiftool_path:
            try:
                result = subprocess.run(
                    [self.exiftool_path, "-ver"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
                ver = result.stdout.strip()
                deps.append(("ExifTool", ver, True))
            except:
                deps.append(("ExifTool", "Found", True))
        else:
            deps.append(("ExifTool", "Not found", False))

        # PyWin32
        if HAS_WIN32COM:
            deps.append(("PyWin32", "Installed", True))
        else:
            deps.append(("PyWin32", "Not installed", False))

        # ttkbootstrap
        try:
            import ttkbootstrap
            deps.append(("ttkbootstrap", ttkbootstrap.__version__, True))
        except:
            deps.append(("ttkbootstrap", "Unknown", True))

        # Platform
        deps.append(("Platform", f"{platform.system()} {platform.release()}", True))

        return deps

