#!/usr/bin/env python3
"""
Canon Shutter Counter Pro - Main Application
Professional tool for reading Canon camera shutter counts

Author: Noel Wangler - NoW Photography
Website: noelwangler.ch
Version: 2.0
"""

import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import os
import sys

# Import our modules
from camera_metadata import CameraMetadataReader, USBCameraDetector, DependencyChecker
from ui_components import TabFactory, DependencyRowWidget, Theme, RoundedButton


class CanonShutterCounter:
    """Main application class"""

    def __init__(self, root):
        self.root = root
        self.root.title("Canon Shutter Counter Pro")

        # Window settings
        self.root.geometry("1280x820")
        self.root.minsize(900, 620)

        # Theme state – start dark
        self.is_dark_mode = True
        Theme.set_dark()
        self.root.configure(bg=Theme.get("bg"))

        # Load icon
        self.logo_image = self._load_icon()

        # Initialize backend components
        self.metadata_reader = CameraMetadataReader()
        self.usb_detector    = USBCameraDetector()
        self.dependency_checker = DependencyChecker(self.metadata_reader.exiftool_path)

        # Processing state
        self.processing = False

        # UI References
        self.ui_widgets = {}

        # Create UI
        self.create_ui()

    # ------------------------------------------------------------------
    def _load_icon(self):
        # Resolve base path: PyInstaller bundle uses _MEIPASS, else script dir
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS
        else:
            base = os.path.dirname(os.path.abspath(__file__))

        # Set .ico as window icon (Windows taskbar / title bar)
        ico_path = os.path.join(base, "Icon", "now_shuttercount.ico")
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                pass

        # Load PNG for iconphoto (high-DPI title bar icon)
        png_path = os.path.join(base, "Icon", "now_shuttercount.png")
        if os.path.exists(png_path):
            try:
                icon = tk.PhotoImage(file=png_path)
                self.root.iconphoto(True, icon)
                return icon
            except Exception:
                pass
        return None

    # ------------------------------------------------------------------
    def toggle_theme(self):
        """Switch between dark and light mode and rebuild the entire UI."""
        if self.is_dark_mode:
            Theme.set_light()
            self.is_dark_mode = False
            self.root.style.theme_use("flatly")
        else:
            Theme.set_dark()
            self.is_dark_mode = True
            self.root.style.theme_use("darkly")

        # Destroy and rebuild everything
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg=Theme.get("bg"))
        self.ui_widgets = {}
        self.processing  = False
        self.create_ui()

    # ------------------------------------------------------------------
    def create_ui(self):
        """Create the main user interface."""
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # ---- Header bar ----
        header = tk.Frame(self.root, bg=Theme.get("header_bg"),
                          padx=Theme.PAD_LG, pady=12)
        header.grid(row=0, column=0, sticky=EW)
        header.columnconfigure(1, weight=1)

        # Logo / title group
        title_group = tk.Frame(header, bg=Theme.get("header_bg"))
        title_group.grid(row=0, column=0, sticky=W)

        # Accent dot
        tk.Frame(title_group, width=4, bg=Theme.get("accent")).pack(
            side=LEFT, fill=Y, padx=(0, 10))

        tk.Label(title_group,
                 text="Canon Shutter Counter Pro",
                 font=("Segoe UI", 16, "bold"),
                 fg=Theme.get("text"),
                 bg=Theme.get("header_bg")).pack(side=LEFT)

        tk.Label(title_group,
                 text="  ·  Professional Camera Analysis",
                 font=("Segoe UI", 10),
                 fg=Theme.get("text_muted"),
                 bg=Theme.get("header_bg")).pack(side=LEFT, pady=(2, 0))

        # Theme toggle button (right side)
        btn_label = "Light Mode" if self.is_dark_mode else "Dark Mode"
        self.theme_button = RoundedButton(
            header, text=btn_label,
            command=self.toggle_theme,
            variant="secondary",
            width=120, height=32)
        self.theme_button.grid(row=0, column=2, sticky=E)

        # thin accent line under header
        tk.Frame(self.root, height=1, bg=Theme.get("accent")).grid(
            row=0, column=0, sticky=(S, E, W))

        # ---- Notebook ----
        style = ttk.Style()
        nb_bg      = Theme.get("bg")
        nb_tab_bg  = Theme.get("surface")
        nb_sel     = Theme.get("surface")
        nb_fg      = Theme.get("text_muted")
        nb_sel_fg  = Theme.get("text")

        style.configure("Custom.TNotebook",
                         background=nb_bg,
                         borderwidth=0,
                         tabmargins=[0, 4, 0, 0])
        style.configure("Custom.TNotebook.Tab",
                         background=nb_tab_bg,
                         foreground=nb_fg,
                         font=Theme.FONT_BODY,
                         padding=[14, 7],
                         borderwidth=0)
        style.map("Custom.TNotebook.Tab",
                  background=[("selected", nb_sel)],
                  foreground=[("selected", nb_sel_fg)])

        self.notebook = ttk.Notebook(self.root, style="Custom.TNotebook")
        self.notebook.grid(row=1, column=0, sticky=NSEW,
                           padx=0, pady=0)

        self._create_all_tabs()

        # ---- Status bar ----
        status_bar = tk.Frame(self.root,
                              bg=Theme.get("status_bg"),
                              padx=Theme.PAD_LG, pady=6)
        status_bar.grid(row=2, column=0, sticky=EW)
        status_bar.columnconfigure(1, weight=1)

        # left status dot + text
        self._status_dot = tk.Frame(status_bar, width=8, height=8,
                                    bg=Theme.get("success"))
        self._status_dot.pack(side=LEFT, padx=(0, 8), pady=3)

        self.status_label = tk.Label(status_bar,
                                     text="Ready",
                                     font=Theme.FONT_SMALL,
                                     fg=Theme.get("text_muted"),
                                     bg=Theme.get("status_bg"))
        self.status_label.pack(side=LEFT)

        self.progress_bar = ttk.Progressbar(status_bar,
                                            bootstyle="success-striped",
                                            mode='indeterminate',
                                            length=200)

    # ------------------------------------------------------------------
    def _create_all_tabs(self):
        file_callbacks  = {'select_files': self.select_files}
        usb_callbacks   = {'read_usb_camera': self.read_usb_camera,
                           'detect_camera':   self.detect_camera}
        batch_callbacks = {'batch_process_folder':  self.batch_process_folder,
                           'batch_process_current': self.batch_process_current}
        tools_callbacks = {'check_dependencies': self.check_dependencies}

        self.ui_widgets.update(
            TabFactory.create_file_reader_tab(self.notebook, file_callbacks))
        self.ui_widgets.update(
            TabFactory.create_usb_reader_tab(self.notebook, usb_callbacks))
        self.ui_widgets.update(
            TabFactory.create_batch_processor_tab(self.notebook, batch_callbacks))
        self.ui_widgets.update(
            TabFactory.create_tools_tab(self.notebook, tools_callbacks))
        TabFactory.create_info_tab(self.notebook, self.logo_image)

    # ------------------------------------------------------------------
    def update_status(self, message, show_progress=False):
        self.status_label.config(text=message)
        dot_color = Theme.get("warning") if show_progress else Theme.get("success")
        self._status_dot.config(bg=dot_color)

        if show_progress and not self.processing:
            self.progress_bar.pack(side=RIGHT, padx=(0, 0))
            self.progress_bar.start(10)
            self.processing = True
        elif not show_progress and self.processing:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.processing = False

        self.root.update_idletasks()

    # ===== FILE READER =================================================

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select CR3 Files",
            filetypes=[("CR3 files", "*.CR3 *.cr3"), ("All files", "*.*")]
        )
        if not files:
            return

        result_text = self.ui_widgets['file_result_text']
        count_label = self.ui_widgets['file_count_label']

        result_text.delete('1.0', tk.END)
        self.update_status(f"Processing {len(files)} file(s)…", True)
        count_label.config(text=f"0 / {len(files)}")

        def process():
            results = []
            for idx, file_path in enumerate(files, 1):
                self.root.after(0, lambda i=idx, t=len(files):
                    count_label.config(text=f"{i} / {t}"))
                metadata = self.metadata_reader.get_camera_metadata(file_path)
                output   = CameraMetadataReader.format_metadata_output(
                    os.path.basename(file_path), metadata)
                results.append(output)

            out = "\n\n".join(results)
            self.root.after(0, lambda: result_text.insert('1.0', out))
            self.root.after(0, lambda: count_label.config(
                text=f"{len(files)} file(s) processed"))
            self.root.after(0, lambda: self.update_status(
                f"Complete — {len(files)} file(s) processed", False))

        threading.Thread(target=process, daemon=True).start()

    # ===== USB CAMERA ==================================================

    def detect_camera(self):
        result_text = self.ui_widgets['usb_result_text']
        result_text.delete('1.0', tk.END)
        self.update_status("Detecting camera…", True)

        def detect():
            result = self.usb_detector.detect_camera()
            self.root.after(0, lambda: result_text.insert('1.0', result))
            self.root.after(0, lambda: self.update_status("Detection complete", False))

        threading.Thread(target=detect, daemon=True).start()

    def read_usb_camera(self):
        result_text = self.ui_widgets['usb_result_text']
        result_text.delete('1.0', tk.END)
        self.update_status("Reading camera…", True)

        def read():
            result = self.usb_detector.read_usb_camera()
            self.root.after(0, lambda: result_text.insert('1.0', result))
            self.root.after(0, lambda: self.update_status("Reading complete", False))

        threading.Thread(target=read, daemon=True).start()

    # ===== BATCH =======================================================

    def batch_process_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self._process_folder(folder)

    def batch_process_current(self):
        self._process_folder(os.getcwd())

    def _process_folder(self, folder_path):
        result_text  = self.ui_widgets['batch_result_text']
        count_label  = self.ui_widgets['batch_count_label']
        progress_bar = self.ui_widgets['batch_progress']

        result_text.delete('1.0', tk.END)
        self.update_status("Scanning folder…", True)
        progress_bar['value'] = 0

        def process():
            cr3_files = self.metadata_reader.batch_process_folder(folder_path)

            if not cr3_files:
                msg = (f"No CR3 files found in:\n{folder_path}")
                self.root.after(0, lambda: result_text.insert('1.0', msg))
                self.root.after(0, lambda: self.update_status("No files found", False))
                self.root.after(0, lambda: count_label.config(text=""))
                return

            results = [f"Folder: {folder_path}",
                       f"Found:  {len(cr3_files)} CR3 file(s)\n",
                       "─" * 62 + "\n"]

            for idx, file_path in enumerate(cr3_files, 1):
                progress = (idx / len(cr3_files)) * 100
                self.root.after(0, lambda p=progress:
                    progress_bar.configure(value=p))
                self.root.after(0, lambda i=idx, t=len(cr3_files):
                    count_label.config(text=f"{i} / {t}"))
                metadata = self.metadata_reader.get_camera_metadata(str(file_path))
                output   = CameraMetadataReader.format_metadata_output(
                    file_path.name, metadata)
                results.append(output)
                results.append("")

            out = "\n".join(results)
            self.root.after(0, lambda: result_text.insert('1.0', out))
            self.root.after(0, lambda: count_label.config(
                text=f"{len(cr3_files)} file(s) processed"))
            self.root.after(0, lambda: self.update_status(
                f"Complete — {len(cr3_files)} file(s) processed", False))

        threading.Thread(target=process, daemon=True).start()

    # ===== DEPENDENCIES ================================================

    def check_dependencies(self):
        dep_frame = self.ui_widgets['dependency_frame']
        for w in dep_frame.winfo_children():
            w.destroy()
        self.update_status("Checking dependencies…", True)

        def check():
            deps = self.dependency_checker.check_all()
            for name, value, status in deps:
                self.root.after(0, lambda n=name, v=value, s=status:
                    DependencyRowWidget.create(dep_frame, n, v, s))
            self.root.after(0, lambda:
                self.update_status("Dependencies checked", False))

        threading.Thread(target=check, daemon=True).start()


# -----------------------------------------------------------------------

def main():
    root = ttk.Window(themename="darkly")
    app  = CanonShutterCounter(root)
    root.mainloop()


if __name__ == "__main__":
    main()

