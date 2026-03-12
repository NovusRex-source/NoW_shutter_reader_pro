#!/usr/bin/env python3

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
try:
    from ttkbootstrap.widgets import ToolTip
except ImportError:
    ToolTip = None
import threading
import subprocess
import os
import sys
import shutil
import webbrowser
import platform
from pathlib import Path

try:
    import win32com.client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False


class CanonShutterCounter:
    def __init__(self, root):
        self.root = root
        self.root.title("Canon Shutter Counter Pro")

        # Responsive Window Settings
        self.root.geometry("1280x800")
        self.root.minsize(900, 600)

        # Dark/Light Mode State
        self.is_dark_mode = True
        self.current_theme = "darkly"

        # Load icon
        icon_path = os.path.join("Icon", "now_shuttercount.png")
        if os.path.exists(icon_path):
            try:
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
                self.logo_image = icon
            except:
                self.logo_image = None
        else:
            self.logo_image = None
        
        self.exiftool_path = self.find_exiftool()
        self.processing = False
        
        self.create_ui()

    def toggle_theme(self):
        """Toggle between dark and light mode"""
        if self.is_dark_mode:
            self.current_theme = "flatly"
            self.is_dark_mode = False
            button_text = "🌙 Dark Mode"
        else:
            self.current_theme = "darkly"
            self.is_dark_mode = True
            button_text = "☀️ Light Mode"

        # Apply new theme
        self.root.style.theme_use(self.current_theme)
        self.theme_button.config(text=button_text)

    def create_ui(self):
        # Main container with grid for responsiveness
        container = ttk.Frame(self.root)
        container.grid(row=0, column=0, sticky=(N, S, E, W))
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Clean modern header
        header = ttk.Frame(container, bootstyle="primary", padding=15)
        header.grid(row=0, column=0, sticky=(E, W))
        header.grid_columnconfigure(0, weight=1)

        # Header content
        header_left = ttk.Frame(header)
        header_left.grid(row=0, column=0, sticky=W)

        ttk.Label(header_left, text="Canon Shutter Counter Pro",
                 font=("Segoe UI", 24, "bold")).pack(side=LEFT, padx=(0, 15))

        ttk.Label(header_left, text="Professional Camera Analysis",
                 font=("Segoe UI", 10)).pack(side=LEFT, pady=5)

        # Theme Toggle Button (right side)
        self.theme_button = ttk.Button(header,
                                       text="☀️ Light Mode",
                                       command=self.toggle_theme,
                                       bootstyle="outline",
                                       width=14)
        self.theme_button.grid(row=0, column=1, sticky=E, padx=5)

        # Notebook with responsive tabs
        self.notebook = ttk.Notebook(container)
        self.notebook.grid(row=1, column=0, sticky=(N, S, E, W), padx=15, pady=10)

        self.create_file_reader_tab()
        self.create_usb_reader_tab()
        self.create_batch_processor_tab()
        self.create_tools_tab()
        self.create_info_tab()
        
        # Clean status bar
        status_bar = ttk.Frame(container, bootstyle="secondary", padding=10)
        status_bar.grid(row=2, column=0, sticky=(E, W))

        self.status_label = ttk.Label(status_bar, text="Ready", 
                                      font=("Segoe UI", 9))
        self.status_label.pack(side=LEFT)
        
        self.progress_bar = ttk.Progressbar(status_bar, bootstyle="success-striped", 
                                           mode='indeterminate', length=200)

    def create_file_reader_tab(self):
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="  📁 File Reader  ")

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        # Modern card with subtle shadow effect
        card = ttk.Frame(tab, bootstyle="light", padding=25, relief=FLAT)
        card.grid(row=0, column=0, sticky=EW, pady=(0, 15))

        ttk.Label(card, text="Read CR3 File Metadata",
                 font=("Segoe UI", 20, "bold")).pack(anchor=W, pady=(0, 8))

        ttk.Label(card, text="Select Canon RAW files to extract shutter count and camera information",
                 font=("Segoe UI", 10)).pack(anchor=W, pady=(0, 15))

        btn_frame = ttk.Frame(card)
        btn_frame.pack(anchor=W, pady=(0, 5))

        select_btn = ttk.Button(btn_frame, text="📂 Select Files",
                               command=self.select_files, bootstyle="primary",
                               width=20)
        select_btn.pack(side=LEFT, padx=(0, 10))

        clear_btn = ttk.Button(btn_frame, text="🗑️ Clear",
                              command=lambda: self.file_result_text.delete('1.0', tk.END),
                              bootstyle="secondary-outline", width=15)
        clear_btn.pack(side=LEFT)
        
        # Results card
        result_card = ttk.Frame(tab, bootstyle="light", padding=15, relief=FLAT)
        result_card.grid(row=1, column=0, sticky=NSEW)
        result_card.grid_rowconfigure(1, weight=1)
        result_card.grid_columnconfigure(0, weight=1)
        
        header_frame = ttk.Frame(result_card)
        header_frame.grid(row=0, column=0, sticky=EW, pady=(0, 10))

        ttk.Label(header_frame, text="Results", 
                 font=("Segoe UI", 14, "bold")).pack(side=LEFT)

        self.file_count_label = ttk.Label(header_frame, text="", 
                                          font=("Segoe UI", 9), bootstyle="info")
        self.file_count_label.pack(side=RIGHT)
        
        text_frame = ttk.Frame(result_card, relief=SOLID, borderwidth=1)
        text_frame.grid(row=1, column=0, sticky=NSEW)
        
        self.file_result_text = scrolledtext.ScrolledText(
            text_frame, font=("Consolas", 10), wrap=WORD,
            relief=FLAT, padx=15, pady=15)
        self.file_result_text.pack(fill=BOTH, expand=YES)
        
    def create_usb_reader_tab(self):
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="  📷 USB Camera  ")

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        card = ttk.Frame(tab, bootstyle="light", padding=25, relief=FLAT)
        card.grid(row=0, column=0, sticky=EW, pady=(0, 15))

        ttk.Label(card, text="Connected Camera Detection",
                 font=("Segoe UI", 20, "bold")).pack(anchor=W, pady=(0, 8))

        ttk.Label(card, text="Connect your Canon camera via USB and ensure it's powered on",
                 font=("Segoe UI", 10)).pack(anchor=W, pady=(0, 15))

        btn_frame = ttk.Frame(card)
        btn_frame.pack(anchor=W, pady=(0, 10))

        read_btn = ttk.Button(btn_frame, text="📸 Read Camera",
                             command=self.read_usb_camera, bootstyle="success",
                             width=18)
        read_btn.pack(side=LEFT, padx=(0, 10))

        detect_btn = ttk.Button(btn_frame, text="🔍 Detect",
                               command=self.detect_camera, bootstyle="info",
                               width=15)
        detect_btn.pack(side=LEFT, padx=(0, 10))

        clear_btn = ttk.Button(btn_frame, text="🗑️ Clear",
                              command=lambda: self.usb_result_text.delete('1.0', tk.END),
                              bootstyle="secondary-outline", width=12)
        clear_btn.pack(side=LEFT)
        
        alert = ttk.Frame(card, bootstyle="warning", padding=12, relief=FLAT)
        alert.pack(fill=X, pady=(5, 0))

        ttk.Label(alert, text="Note: Canon R-series cameras typically require EOSInfo or Canon EOS Utility for USB shutter count reading",
                 font=("Segoe UI", 9), wraplength=900).pack()

        result_card = ttk.Frame(tab, bootstyle="light", padding=15, relief=FLAT)
        result_card.grid(row=1, column=0, sticky=NSEW)
        result_card.grid_rowconfigure(1, weight=1)
        result_card.grid_columnconfigure(0, weight=1)
        
        ttk.Label(result_card, text="Camera Information", 
                 font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky=W, pady=(0, 10))

        text_frame = ttk.Frame(result_card, relief=SOLID, borderwidth=1)
        text_frame.grid(row=1, column=0, sticky=NSEW)
        
        self.usb_result_text = scrolledtext.ScrolledText(
            text_frame, font=("Consolas", 10), wrap=WORD,
            relief=FLAT, padx=15, pady=15)
        self.usb_result_text.pack(fill=BOTH, expand=YES)
        
    def create_batch_processor_tab(self):
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="  ⚡ Batch Process  ")

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        card = ttk.Frame(tab, bootstyle="light", padding=25, relief=FLAT)
        card.grid(row=0, column=0, sticky=EW, pady=(0, 15))

        ttk.Label(card, text="Bulk File Processing",
                 font=("Segoe UI", 20, "bold")).pack(anchor=W, pady=(0, 8))

        ttk.Label(card, text="Process all CR3 files in a selected folder automatically",
                 font=("Segoe UI", 10)).pack(anchor=W, pady=(0, 15))

        btn_frame = ttk.Frame(card)
        btn_frame.pack(anchor=W, pady=(0, 10))
        
        folder_btn = ttk.Button(btn_frame, text="📂 Select Folder",
                               command=self.batch_process_folder, bootstyle="warning",
                               width=18)
        folder_btn.pack(side=LEFT, padx=(0, 10))

        current_btn = ttk.Button(btn_frame, text="📍 Current Folder",
                                command=self.batch_process_current, bootstyle="warning-outline",
                                width=18)
        current_btn.pack(side=LEFT, padx=(0, 10))

        clear_btn = ttk.Button(btn_frame, text="🗑️ Clear",
                              command=lambda: self.batch_result_text.delete('1.0', tk.END),
                              bootstyle="secondary-outline", width=12)
        clear_btn.pack(side=LEFT)
        
        self.batch_progress = ttk.Progressbar(card, bootstyle="success-striped", mode='determinate')
        self.batch_progress.pack(fill=X, pady=(10, 0))
        
        result_card = ttk.Frame(tab, bootstyle="light", padding=15, relief=FLAT)
        result_card.grid(row=1, column=0, sticky=NSEW)
        result_card.grid_rowconfigure(1, weight=1)
        result_card.grid_columnconfigure(0, weight=1)
        
        header_frame = ttk.Frame(result_card)
        header_frame.grid(row=0, column=0, sticky=EW, pady=(0, 10))

        ttk.Label(header_frame, text="Batch Results", 
                 font=("Segoe UI", 14, "bold")).pack(side=LEFT)

        self.batch_count_label = ttk.Label(header_frame, text="", 
                                          font=("Segoe UI", 9), bootstyle="success")
        self.batch_count_label.pack(side=RIGHT)
        
        text_frame = ttk.Frame(result_card, relief=SOLID, borderwidth=1)
        text_frame.grid(row=1, column=0, sticky=NSEW)
        
        self.batch_result_text = scrolledtext.ScrolledText(
            text_frame, font=("Consolas", 9), wrap=WORD,
            relief=FLAT, padx=15, pady=15)
        self.batch_result_text.pack(fill=BOTH, expand=YES)
        
    def create_tools_tab(self):
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="  🔧 Tools  ")

        tab.grid_columnconfigure(0, weight=1)
        
        tools_card = ttk.Frame(tab, bootstyle="light", padding=25, relief=FLAT)
        tools_card.grid(row=0, column=0, sticky=EW, pady=(0, 15))

        ttk.Label(tools_card, text="External Resources",
                 font=("Segoe UI", 20, "bold")).pack(anchor=W, pady=(0, 20))

        self.create_link_card(tools_card, "EOSInfo (Recommended)", 
                             "Windows utility for reliable Canon shutter count reading",
                             "http://www.astrojargon.net/eosinfo.aspx")
        
        self.create_link_card(tools_card, "Canon EOS Utility", 
                             "Official Canon camera management software",
                             "https://www.canon-europe.com/support/consumer/products/cameras/")
        
        self.create_link_card(tools_card, "ExifTool", 
                             "Professional metadata extraction tool by Phil Harvey",
                             "https://exiftool.org/")
        
        info_card = ttk.Frame(tab, bootstyle="light", padding=25, relief=FLAT)
        info_card.grid(row=1, column=0, sticky=EW, pady=(0, 15))

        ttk.Label(info_card, text="System Information",
                 font=("Segoe UI", 20, "bold")).pack(anchor=W, pady=(0, 15))

        check_btn = ttk.Button(info_card, text="🔍 Check Dependencies",
                              command=self.check_dependencies, bootstyle="info",
                              width=25)
        check_btn.pack(anchor=W, pady=(0, 10))

        self.dependency_frame = ttk.Frame(info_card)
        self.dependency_frame.pack(fill=X, anchor=W)
        
    def create_link_card(self, parent, title, description, url):
        card = ttk.Frame(parent, bootstyle="info", padding=20, relief=FLAT)
        card.pack(fill=X, pady=(0, 12))

        content = ttk.Frame(card)
        content.pack(fill=X)
        
        left_frame = ttk.Frame(content)
        left_frame.pack(side=LEFT, fill=X, expand=YES)
        
        title_label = ttk.Label(left_frame, text=title,
                               font=("Segoe UI", 13, "bold"))
        title_label.pack(anchor=W)
        
        desc_label = ttk.Label(left_frame, text=description,
                              font=("Segoe UI", 10),
                              wraplength=650)
        desc_label.pack(anchor=W, pady=(5, 0))

        btn = ttk.Button(content, text="🔗 Open", command=lambda: webbrowser.open(url),
                        bootstyle="light-outline", width=12)
        btn.pack(side=RIGHT, pady=10)

    def create_info_tab(self):
        tab = ttk.Frame(self.notebook, padding=45)
        self.notebook.add(tab, text="   Info   ")
        
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        scroll = ttk.Scrollbar(tab, orient=VERTICAL)
        scroll.grid(row=0, column=1, sticky=NS)
        
        canvas = tk.Canvas(tab, yscrollcommand=scroll.set, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky=NSEW)
        scroll.config(command=canvas.yview)
        
        content_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor=NW)
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
        
        content_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)
        
        center_card = ttk.Frame(content_frame, bootstyle="light", padding=50)
        center_card.pack(pady=25, padx=25, fill=X)
        
        if self.logo_image:
            logo_label = ttk.Label(center_card, image=self.logo_image)
            logo_label.pack(pady=(0, 20))
        
        ttk.Label(center_card, text="Canon Shutter Counter Pro",
                 font=("Helvetica", 36, "bold"), bootstyle="primary").pack(pady=(0, 8))
        
        version_badge = ttk.Label(center_card, text="v2.0 Professional Edition", 
                                 font=("Helvetica", 12, "bold"), bootstyle="success")
        version_badge.pack(pady=(0, 35))
        
        info_card = ttk.Frame(center_card, bootstyle="primary", padding=28)
        info_card.pack(fill=X, pady=(0, 22))
        
        ttk.Label(info_card, text="Supported Cameras",
                 font=("Helvetica", 16, "bold"), foreground="white").pack(anchor=W, pady=(0, 12))

        cameras = "Canon EOS R1, R3, R5, R5 II, R6, R6 II, R6 III, R8, RP"
        ttk.Label(info_card, text=cameras,
                 font=("Helvetica", 11), foreground="white", wraplength=650).pack(anchor=W, padx=20)

        feature_card = ttk.Frame(center_card, bootstyle="success", padding=28)
        feature_card.pack(fill=X, pady=(0, 22))
        
        ttk.Label(feature_card, text="Features",
                 font=("Helvetica", 16, "bold"), foreground="white").pack(anchor=W, pady=(0, 12))

        features = [
            "CR3 file metadata extraction",
            "USB camera detection & reading",
            "Batch folder processing",
            "Model-specific shutter ratings",
            "Professional modern interface"
        ]
        
        for feature in features:
            ttk.Label(feature_card, text=f"• {feature}",
                     font=("Helvetica", 11), foreground="white").pack(anchor=W, padx=20, pady=3)

        req_card = ttk.Frame(center_card, bootstyle="warning", padding=28)
        req_card.pack(fill=X, pady=(0, 22))
        
        ttk.Label(req_card, text="Requirements",
                 font=("Helvetica", 16, "bold"), foreground="white").pack(anchor=W, pady=(0, 12))

        requirements = [
            "Python 3.8 or higher",
            "ExifTool (for file reading)",
            "PyWin32 (for Windows USB detection)",
            "ttkbootstrap (modern UI framework)"
        ]
        
        for req in requirements:
            ttk.Label(req_card, text=f"• {req}",
                     font=("Helvetica", 11), foreground="white").pack(anchor=W, padx=20, pady=3)

        note_card = ttk.Frame(center_card, bootstyle="danger", padding=28)
        note_card.pack(fill=X, pady=(0, 22))

        ttk.Label(note_card, text="Important Note",
                 font=("Helvetica", 16, "bold"), foreground="white").pack(anchor=W, pady=(0, 12))

        note_text = "Canon R-series cameras typically do not store shutter count in CR3 file EXIF data. For accurate shutter count reading, use USB connection with EOSInfo or Canon EOS Utility."
        ttk.Label(note_card, text=note_text,
                 font=("Helvetica", 11), foreground="white",
                 wraplength=650, justify=LEFT).pack(anchor=W, padx=20)

        # Credits Section
        credits_card = ttk.Frame(center_card, bootstyle="info", padding=28)
        credits_card.pack(fill=X)

        ttk.Label(credits_card, text="Credits & Attribution",
                 font=("Helvetica", 16, "bold")).pack(anchor=W, pady=(0, 12))

        ttk.Label(credits_card, text="Developer",
                 font=("Helvetica", 12, "bold")).pack(anchor=W, padx=20, pady=(8, 4))
        ttk.Label(credits_card, text="Noel Wangler - NoW Photography",
                 font=("Helvetica", 11)).pack(anchor=W, padx=40, pady=2)

        website_frame = ttk.Frame(credits_card)
        website_frame.pack(anchor=W, padx=40, pady=(2, 12))
        ttk.Label(website_frame, text="Website: ",
                 font=("Helvetica", 11)).pack(side=LEFT)
        website_link = ttk.Label(website_frame, text="noelwangler.ch",
                               font=("Helvetica", 11, "underline"), cursor="hand2", foreground="blue")
        website_link.pack(side=LEFT)
        website_link.bind("<Button-1>", lambda e: webbrowser.open("https://noelwangler.ch"))

        ttk.Label(credits_card, text="Software Components",
                 font=("Helvetica", 12, "bold")).pack(anchor=W, padx=20, pady=(12, 4))

        components = [
            ("ExifTool", "Phil Harvey"),
            ("Python", "Python Software Foundation"),
            ("ttkbootstrap", "Israel Dryer"),
            ("PyWin32", "Mark Hammond"),
            ("Tkinter", "Python Standard Library")
        ]

        for comp_name, comp_author in components:
            comp_frame = ttk.Frame(credits_card)
            comp_frame.pack(anchor=W, padx=40, pady=2)
            ttk.Label(comp_frame, text=f"• {comp_name}",
                     font=("Helvetica", 10)).pack(side=LEFT)
            ttk.Label(comp_frame, text=f" by {comp_author}",
                     font=("Helvetica", 10)).pack(side=LEFT)

    def update_status(self, message, show_progress=False):
        self.status_label.config(text=message)
        
        if show_progress and not self.processing:
            self.progress_bar.pack(side=RIGHT, padx=10)
            self.progress_bar.start(10)
            self.processing = True
        elif not show_progress and self.processing:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.processing = False
        
        self.root.update_idletasks()
    
    def find_exiftool(self):
        exiftool = shutil.which("exiftool")
        if exiftool:
            return exiftool
        
        for name in ["exiftool.exe", "exiftool"]:
            if os.path.exists(name):
                return name
        
        return None
    
    def get_camera_shutter_rating(self, model):
        if not model:
            return 200000
        
        model_upper = model.upper()
        
        if any(x in model_upper for x in ['R1', 'R3']):
            return 500000
        if any(x in model_upper for x in ['R5', 'R6 II', 'R6 III']):
            return 500000
        
        return 200000
    
    def get_camera_metadata(self, image_path):
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
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, timeout=10,
                                  creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            
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
                metadata["shutter_rating"] = self.get_camera_shutter_rating(metadata["camera_model"])
            
            if metadata["shutter_count"] is None:
                if metadata["camera_model"] and any(x in metadata["camera_model"].upper() 
                    for x in ['R5', 'R6', 'R3', 'R1', 'R8', 'RP']):
                    metadata["error"] = f"Shutter count not in EXIF for {metadata['camera_model']}. Use EOSInfo or Canon EOS Utility."
                else:
                    metadata["error"] = "Shutter count not found in file."
                    
        except subprocess.TimeoutExpired:
            metadata["error"] = "ExifTool timed out"
        except Exception as e:
            metadata["error"] = f"Error: {str(e)}"
        
        return metadata
    
    def format_metadata_output(self, filename, metadata):
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
                lines.append(f"║ Shutter:   {count:,} actuations{' ' * (34 - len(str(count)))}║")
                
                rating = metadata.get("shutter_rating", 200000)
                wear = (count / rating) * 100
                bar_length = 30
                filled = int((wear / 100) * bar_length)
                bar = "█" * filled + "░" * (bar_length - filled)
                lines.append(f"║ Wear:      {wear:5.1f}% [{bar}] ║")
                lines.append(f"║            (rated for {rating:,} actuations){' ' * (24 - len(str(rating)))}║")
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
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select CR3 Files",
            filetypes=[("CR3 files", "*.CR3 *.cr3"), ("All files", "*.*")]
        )
        
        if not files:
            return
        
        self.file_result_text.delete('1.0', tk.END)
        self.update_status(f"Processing {len(files)} file(s)...", True)
        self.file_count_label.config(text=f"Processing 0/{len(files)}")
        
        def process():
            results = []
            for idx, file_path in enumerate(files, 1):
                self.root.after(0, lambda i=idx, t=len(files): 
                    self.file_count_label.config(text=f"Processing {i}/{t}"))
                
                metadata = self.get_camera_metadata(file_path)
                output = self.format_metadata_output(os.path.basename(file_path), metadata)
                results.append(output)
            
            result_text = "\n\n".join(results)
            self.root.after(0, lambda: self.file_result_text.insert('1.0', result_text))
            self.root.after(0, lambda: self.file_count_label.config(text=f"{len(files)} files processed"))
            self.root.after(0, lambda: self.update_status(f"Complete - Processed {len(files)} files", False))
        
        threading.Thread(target=process, daemon=True).start()
    
    def detect_camera(self):
        self.usb_result_text.delete('1.0', tk.END)
        self.update_status("Detecting camera...", True)
        
        def detect():
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
            
            result_text = "\n".join(result_lines)
            self.root.after(0, lambda: self.usb_result_text.insert('1.0', result_text))
            self.root.after(0, lambda: self.update_status("Detection complete", False))
        
        threading.Thread(target=detect, daemon=True).start()
    
    def read_usb_camera(self):
        self.usb_result_text.delete('1.0', tk.END)
        self.update_status("Reading camera...", True)
        
        def read():
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
            
            result_text = "\n".join(result_lines)
            self.root.after(0, lambda: self.usb_result_text.insert('1.0', result_text))
            self.root.after(0, lambda: self.update_status("Reading complete", False))
        
        threading.Thread(target=read, daemon=True).start()
    
    def batch_process_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self._process_folder(folder)
    
    def batch_process_current(self):
        self._process_folder(os.getcwd())
    
    def _process_folder(self, folder_path):
        self.batch_result_text.delete('1.0', tk.END)
        self.update_status("Scanning folder...", True)
        self.batch_progress['value'] = 0
        
        def process():
            cr3_files = list(Path(folder_path).glob("*.CR3")) + list(Path(folder_path).glob("*.cr3"))
            
            if not cr3_files:
                result = f"╔══════════════════════════════════════════════════════════╗\n"
                result += f"║ No CR3 files found in folder                             ║\n"
                result += f"╠══════════════════════════════════════════════════════════╣\n"
                result += f"║ Path: {folder_path[:52]:<52}║\n"
                result += f"╚══════════════════════════════════════════════════════════╝"
                self.root.after(0, lambda: self.batch_result_text.insert('1.0', result))
                self.root.after(0, lambda: self.update_status("No files found", False))
                self.root.after(0, lambda: self.batch_count_label.config(text=""))
                return
            
            results = [f"Processing {len(cr3_files)} files from: {folder_path}\n"]
            results.append("=" * 60 + "\n")
            
            for idx, file_path in enumerate(cr3_files, 1):
                progress = (idx / len(cr3_files)) * 100
                self.root.after(0, lambda p=progress: self.batch_progress.configure(value=p))
                self.root.after(0, lambda i=idx, t=len(cr3_files): 
                    self.batch_count_label.config(text=f"Processing {i}/{t}"))
                
                metadata = self.get_camera_metadata(str(file_path))
                output = self.format_metadata_output(file_path.name, metadata)
                results.append(output)
                results.append("\n")
            
            result_text = "\n".join(results)
            self.root.after(0, lambda: self.batch_result_text.insert('1.0', result_text))
            self.root.after(0, lambda: self.batch_count_label.config(text=f"{len(cr3_files)} files processed"))
            self.root.after(0, lambda: self.update_status(f"Complete - Processed {len(cr3_files)} files", False))
        
        threading.Thread(target=process, daemon=True).start()
    
    def check_dependencies(self):
        for widget in self.dependency_frame.winfo_children():
            widget.destroy()
        
        self.update_status("Checking dependencies...", True)
        
        def check():
            deps = []
            
            py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            deps.append(("Python", py_version, True))
            
            if self.exiftool_path:
                try:
                    result = subprocess.run([self.exiftool_path, "-ver"], 
                                          capture_output=True, text=True, timeout=5,
                                          creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
                    ver = result.stdout.strip()
                    deps.append(("ExifTool", ver, True))
                except:
                    deps.append(("ExifTool", "Found", True))
            else:
                deps.append(("ExifTool", "Not found", False))
            
            if HAS_WIN32COM:
                deps.append(("PyWin32", "Installed", True))
            else:
                deps.append(("PyWin32", "Not installed", False))
            
            try:
                import ttkbootstrap
                deps.append(("ttkbootstrap", ttkbootstrap.__version__, True))
            except:
                deps.append(("ttkbootstrap", "Unknown", True))
            
            deps.append(("Platform", f"{platform.system()} {platform.release()}", True))
            
            for name, value, status in deps:
                self.root.after(0, lambda n=name, v=value, s=status: self._add_dep_row(n, v, s))
            
            self.root.after(0, lambda: self.update_status("Dependencies checked", False))
        
        threading.Thread(target=check, daemon=True).start()
    
    def _add_dep_row(self, name, value, status):
        row = ttk.Frame(self.dependency_frame, bootstyle="success" if status else "danger", padding=12)
        row.pack(fill=X, pady=6)
        
        icon = "✓" if status else "✗"

        ttk.Label(row, text=f"{icon} {name}:",
                 font=("Segoe UI", 11, "bold")).pack(side=LEFT)

        ttk.Label(row, text=value,
                 font=("Segoe UI", 11)).pack(side=LEFT, padx=12)


def main():
    root = ttk.Window(themename="darkly")  # Start with dark mode
    app = CanonShutterCounter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
