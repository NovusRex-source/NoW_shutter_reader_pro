#!/usr/bin/env python3
"""
UI Components Module
Handles all user interface elements and layouts
"""

import tkinter as tk
from tkinter import scrolledtext, font as tkfont
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser


# ---------------------------------------------------------------------------
# Design tokens – one place to change colors / sizes
# ---------------------------------------------------------------------------
class Theme:
    """Central design-token registry for both Dark and Light mode."""

    # Fonts
    FONT_TITLE   = ("Segoe UI", 13, "bold")
    FONT_HEADING = ("Segoe UI", 11, "bold")
    FONT_BODY    = ("Segoe UI", 10)
    FONT_SMALL   = ("Segoe UI", 9)
    FONT_MONO    = ("Consolas", 10)

    # Padding / spacing
    PAD_LG = 20
    PAD_MD = 14
    PAD_SM = 8
    PAD_XS = 4

    # Corner radius (used as relief trick via style overrides)
    RADIUS = 6

    DARK = {
        "bg":          "#1e1e2e",   # main window background
        "surface":     "#2a2a3d",   # card / panel background
        "surface2":    "#313146",   # slightly elevated surface
        "border":      "#3d3d5c",   # subtle border
        "accent":      "#7c6af7",   # primary accent (soft violet)
        "accent_hover":"#9585f9",
        "success":     "#4caf87",   # muted green
        "warning":     "#c9943a",   # muted amber
        "danger":      "#c0605a",   # muted red
        "info":        "#4a90c4",   # muted blue
        "text":        "#e2e2f0",   # primary text
        "text_muted":  "#8888aa",   # secondary text
        "btn_fg":      "#ffffff",
        "input_bg":    "#252537",
        "input_border":"#44446a",
        "progress_bg": "#3d3d5c",
        "header_bg":   "#16162a",
        "tab_active":  "#7c6af7",
        "tab_inactive":"#2a2a3d",
        "status_bg":   "#16162a",
    }

    LIGHT = {
        "bg":          "#f4f4f8",
        "surface":     "#ffffff",
        "surface2":    "#eeeef6",
        "border":      "#d4d4e4",
        "accent":      "#5a4fcf",
        "accent_hover":"#6e62e0",
        "success":     "#2e7d5e",
        "warning":     "#b37230",
        "danger":      "#a33d38",
        "info":        "#2c6da0",
        "text":        "#1a1a2e",
        "text_muted":  "#666688",
        "btn_fg":      "#ffffff",
        "input_bg":    "#ffffff",
        "input_border":"#bbbbd0",
        "progress_bg": "#d4d4e4",
        "header_bg":   "#eeeef6",
        "tab_active":  "#5a4fcf",
        "tab_inactive":"#ffffff",
        "status_bg":   "#eeeef6",
    }

    _current = DARK

    @classmethod
    def set_dark(cls):
        cls._current = cls.DARK

    @classmethod
    def set_light(cls):
        cls._current = cls.LIGHT

    @classmethod
    def get(cls, key):
        return cls._current.get(key, "#ff00ff")


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _card(parent, bg_key="surface", pad=None, **kw):
    """Create a flat card-like Frame with themed background."""
    p = pad if pad is not None else Theme.PAD_MD
    f = tk.Frame(parent, bg=Theme.get(bg_key), padx=p, pady=p, **kw)
    return f


def _label(parent, text, font=None, color_key="text", **kw):
    f = font or Theme.FONT_BODY
    return tk.Label(parent, text=text, font=f, fg=Theme.get(color_key),
                    bg=Theme.get("surface"), **kw)


def _divider(parent, bg_key="border"):
    return tk.Frame(parent, height=1, bg=Theme.get(bg_key))


class RoundedButton(tk.Canvas):
    """
    A Canvas-based button with rounded corners, hover effect,
    and full theme support.
    """

    def __init__(self, parent, text, command=None,
                 variant="primary",   # primary | secondary | success | warning | danger | ghost
                 width=140, height=34,
                 radius=8, **kw):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bd=0,
                         bg=parent.cget("bg"), **kw)
        self._text    = text
        self._command = command
        self._variant = variant
        self._width   = width
        self._height  = height
        self._radius  = radius
        self._pressed = False

        self._build()
        self.bind("<Enter>",          self._on_enter)
        self.bind("<Leave>",          self._on_leave)
        self.bind("<ButtonPress-1>",  self._on_press)
        self.bind("<ButtonRelease-1>",self._on_release)

    # ---- color helpers ----
    def _colors(self, hover=False, pressed=False):
        v = self._variant
        t = Theme._current
        if v == "primary":
            bg = t["accent_hover"] if (hover or pressed) else t["accent"]
            fg = t["btn_fg"]
            border = bg
        elif v == "secondary":
            bg = t["surface2"]
            fg = t["text"]
            border = t["border"]
            if hover or pressed:
                bg = t["border"]
        elif v == "success":
            base = t["success"]
            bg = self._lighten(base, 0.08) if hover else base
            fg = t["btn_fg"]; border = bg
        elif v == "warning":
            base = t["warning"]
            bg = self._lighten(base, 0.08) if hover else base
            fg = t["btn_fg"]; border = bg
        elif v == "danger":
            base = t["danger"]
            bg = self._lighten(base, 0.08) if hover else base
            fg = t["btn_fg"]; border = bg
        elif v == "ghost":
            bg = t["surface2"] if hover else t["surface"]
            fg = t["accent"]
            border = t["border"]
        else:
            bg = t["accent"]; fg = t["btn_fg"]; border = bg
        return bg, fg, border

    @staticmethod
    def _lighten(hex_color, factor):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _build(self, hover=False, pressed=False):
        self.delete("all")
        bg, fg, border = self._colors(hover, pressed)
        r  = self._radius
        w  = self._width
        h  = self._height

        # rounded rectangle
        self.create_arc(0,     0,     2*r, 2*r, start=90,  extent=90,  fill=bg, outline=border, width=1)
        self.create_arc(w-2*r, 0,     w,   2*r, start=0,   extent=90,  fill=bg, outline=border, width=1)
        self.create_arc(w-2*r, h-2*r, w,   h,   start=270, extent=90,  fill=bg, outline=border, width=1)
        self.create_arc(0,     h-2*r, 2*r, h,   start=180, extent=90,  fill=bg, outline=border, width=1)
        self.create_rectangle(r, 0,   w-r, h,   fill=bg, outline=bg)
        self.create_rectangle(0, r,   w,   h-r, fill=bg, outline=bg)

        # border lines
        self.create_line(r, 0,   w-r, 0,   fill=border, width=1)
        self.create_line(r, h,   w-r, h,   fill=border, width=1)
        self.create_line(0, r,   0,   h-r, fill=border, width=1)
        self.create_line(w, r,   w,   h-r, fill=border, width=1)

        # label
        self.create_text(w//2, h//2, text=self._text,
                         font=Theme.FONT_BODY, fill=fg, anchor="center")

    def _on_enter(self, _=None):  self._build(hover=True)
    def _on_leave(self, _=None):  self._build()
    def _on_press(self, _=None):
        self._pressed = True
        self._build(pressed=True)
    def _on_release(self, _=None):
        self._pressed = False
        self._build(hover=True)
        if self._command:
            self._command()

    def refresh(self):
        """Call after theme switch to repaint."""
        self.config(bg=self.master.cget("bg"))
        self._build()


# ---------------------------------------------------------------------------
# Reusable themed widgets
# ---------------------------------------------------------------------------

class ThemedText(tk.Frame):
    """
    A themed, resizable text area with scrollbar.
    Exposes .text for direct access.
    """

    def __init__(self, parent, **kw):
        super().__init__(parent,
                         bg=Theme.get("border"),
                         padx=1, pady=1)      # thin border via frame bg

        inner = tk.Frame(self, bg=Theme.get("input_bg"))
        inner.pack(fill=BOTH, expand=YES)

        sb = tk.Scrollbar(inner, orient=VERTICAL,
                          bg=Theme.get("surface2"), troughcolor=Theme.get("bg"),
                          activebackground=Theme.get("border"), bd=0, width=12)
        sb.pack(side=RIGHT, fill=Y)

        self.text = tk.Text(
            inner,
            font=Theme.FONT_MONO,
            bg=Theme.get("input_bg"),
            fg=Theme.get("text"),
            insertbackground=Theme.get("text"),
            selectbackground=Theme.get("accent"),
            selectforeground=Theme.get("btn_fg"),
            relief=FLAT, bd=0,
            padx=14, pady=12,
            wrap=WORD,
            yscrollcommand=sb.set,
            **kw
        )
        self.text.pack(side=LEFT, fill=BOTH, expand=YES)
        sb.config(command=self.text.yview)

    # proxy common Text methods
    def insert(self, *a, **kw): self.text.insert(*a, **kw)
    def delete(self, *a, **kw): self.text.delete(*a, **kw)
    def get(self, *a, **kw):    return self.text.get(*a, **kw)


class SectionHeader(tk.Frame):
    """Section title + optional subtitle inside a card."""

    def __init__(self, parent, title, subtitle="", **kw):
        bg = parent.cget("bg")
        super().__init__(parent, bg=bg, **kw)

        tk.Label(self, text=title, font=Theme.FONT_TITLE,
                 fg=Theme.get("text"), bg=bg).pack(anchor=W)

        if subtitle:
            tk.Label(self, text=subtitle, font=Theme.FONT_SMALL,
                     fg=Theme.get("text_muted"), bg=bg).pack(anchor=W, pady=(2, 0))


class AlertBanner(tk.Frame):
    """A one-line coloured info/warning banner."""

    def __init__(self, parent, text, variant="warning", **kw):
        color_map = {
            "warning": Theme.get("warning"),
            "info":    Theme.get("info"),
            "success": Theme.get("success"),
            "danger":  Theme.get("danger"),
        }
        accent = color_map.get(variant, Theme.get("info"))
        super().__init__(parent, bg=Theme.get("surface2"), **kw)

        # left accent stripe
        tk.Frame(self, width=3, bg=accent).pack(side=LEFT, fill=Y)

        tk.Label(self, text=text, font=Theme.FONT_SMALL,
                 fg=Theme.get("text_muted"), bg=Theme.get("surface2"),
                 wraplength=900, justify=LEFT, padx=10, pady=8).pack(side=LEFT, fill=X, expand=YES)


# ---------------------------------------------------------------------------
# Tab factory
# ---------------------------------------------------------------------------

class TabFactory:
    """Factory for creating themed UI tabs."""

    # ------------------------------------------------------------------ #
    #  File Reader
    # ------------------------------------------------------------------ #
    @staticmethod
    def create_file_reader_tab(notebook, callbacks):
        bg = Theme.get("bg")
        tab = tk.Frame(notebook, bg=bg)
        notebook.add(tab, text="  File Reader  ")

        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)

        # ---- top card ----
        top = _card(tab, bg_key="surface", pad=Theme.PAD_LG)
        top.grid(row=0, column=0, sticky=EW, padx=Theme.PAD_LG, pady=(Theme.PAD_LG, 0))

        SectionHeader(top,
                      title="Read CR3 File Metadata",
                      subtitle="Select Canon RAW files to extract shutter count and camera information"
                      ).pack(anchor=W, pady=(0, Theme.PAD_MD))

        _divider(top).pack(fill=X, pady=(0, Theme.PAD_MD))

        btn_row = tk.Frame(top, bg=Theme.get("surface"))
        btn_row.pack(anchor=W)

        select_btn = RoundedButton(btn_row, text="Select Files",
                                   command=callbacks['select_files'],
                                   variant="primary", width=140, height=34)
        select_btn.grid(row=0, column=0, padx=(0, 8))

        # placeholder – clear button created after text widget
        clear_holder = tk.Frame(btn_row, bg=Theme.get("surface"))
        clear_holder.grid(row=0, column=1)

        # ---- results card ----
        bottom = _card(tab, bg_key="surface", pad=Theme.PAD_MD)
        bottom.grid(row=1, column=0, sticky=NSEW,
                    padx=Theme.PAD_LG, pady=Theme.PAD_SM)
        bottom.rowconfigure(2, weight=1)
        bottom.columnconfigure(0, weight=1)

        result_header = tk.Frame(bottom, bg=Theme.get("surface"))
        result_header.grid(row=0, column=0, sticky=EW, pady=(0, Theme.PAD_XS))
        result_header.columnconfigure(0, weight=1)

        tk.Label(result_header, text="Results", font=Theme.FONT_HEADING,
                 fg=Theme.get("text"), bg=Theme.get("surface")).grid(row=0, column=0, sticky=W)

        file_count_label = tk.Label(result_header, text="",
                                    font=Theme.FONT_SMALL,
                                    fg=Theme.get("text_muted"),
                                    bg=Theme.get("surface"))
        file_count_label.grid(row=0, column=1, sticky=E)

        _divider(bottom).grid(row=1, column=0, sticky=EW, pady=(0, Theme.PAD_SM))

        file_result_text = ThemedText(bottom)
        file_result_text.grid(row=2, column=0, sticky=NSEW)

        # now attach clear button
        RoundedButton(clear_holder, text="Clear",
                      command=lambda: file_result_text.delete('1.0', END),
                      variant="secondary", width=100, height=34).pack()

        return {
            'file_result_text': file_result_text,
            'file_count_label': file_count_label,
        }

    # ------------------------------------------------------------------ #
    #  USB Camera
    # ------------------------------------------------------------------ #
    @staticmethod
    def create_usb_reader_tab(notebook, callbacks):
        bg = Theme.get("bg")
        tab = tk.Frame(notebook, bg=bg)
        notebook.add(tab, text="  USB Camera  ")

        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)

        top = _card(tab, bg_key="surface", pad=Theme.PAD_LG)
        top.grid(row=0, column=0, sticky=EW, padx=Theme.PAD_LG, pady=(Theme.PAD_LG, 0))

        SectionHeader(top,
                      title="Connected Camera Detection",
                      subtitle="Connect your Canon camera via USB and ensure it is powered on"
                      ).pack(anchor=W, pady=(0, Theme.PAD_MD))

        _divider(top).pack(fill=X, pady=(0, Theme.PAD_MD))

        btn_row = tk.Frame(top, bg=Theme.get("surface"))
        btn_row.pack(anchor=W, pady=(0, Theme.PAD_SM))

        RoundedButton(btn_row, text="Read Camera",
                      command=callbacks['read_usb_camera'],
                      variant="success", width=140, height=34).grid(row=0, column=0, padx=(0, 8))
        RoundedButton(btn_row, text="Detect",
                      command=callbacks['detect_camera'],
                      variant="primary", width=110, height=34).grid(row=0, column=1, padx=(0, 8))

        # clear added after text widget
        clear_holder = tk.Frame(btn_row, bg=Theme.get("surface"))
        clear_holder.grid(row=0, column=2)

        AlertBanner(top,
                    text="Note: Canon R-series cameras typically require EOSInfo or Canon EOS Utility for USB shutter count reading.",
                    variant="warning").pack(fill=X, pady=(Theme.PAD_SM, 0))

        bottom = _card(tab, bg_key="surface", pad=Theme.PAD_MD)
        bottom.grid(row=1, column=0, sticky=NSEW,
                    padx=Theme.PAD_LG, pady=Theme.PAD_SM)
        bottom.rowconfigure(2, weight=1)
        bottom.columnconfigure(0, weight=1)

        tk.Label(bottom, text="Camera Information", font=Theme.FONT_HEADING,
                 fg=Theme.get("text"), bg=Theme.get("surface")).grid(row=0, column=0, sticky=W)
        _divider(bottom).grid(row=1, column=0, sticky=EW, pady=(Theme.PAD_XS, Theme.PAD_SM))

        usb_result_text = ThemedText(bottom)
        usb_result_text.grid(row=2, column=0, sticky=NSEW)

        RoundedButton(clear_holder, text="Clear",
                      command=lambda: usb_result_text.delete('1.0', END),
                      variant="secondary", width=100, height=34).pack()

        return {'usb_result_text': usb_result_text}

    # ------------------------------------------------------------------ #
    #  Batch Processor
    # ------------------------------------------------------------------ #
    @staticmethod
    def create_batch_processor_tab(notebook, callbacks):
        bg = Theme.get("bg")
        tab = tk.Frame(notebook, bg=bg)
        notebook.add(tab, text="  Batch Process  ")

        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)

        top = _card(tab, bg_key="surface", pad=Theme.PAD_LG)
        top.grid(row=0, column=0, sticky=EW, padx=Theme.PAD_LG, pady=(Theme.PAD_LG, 0))

        SectionHeader(top,
                      title="Bulk File Processing",
                      subtitle="Process all CR3 files in a selected folder automatically"
                      ).pack(anchor=W, pady=(0, Theme.PAD_MD))

        _divider(top).pack(fill=X, pady=(0, Theme.PAD_MD))

        btn_row = tk.Frame(top, bg=Theme.get("surface"))
        btn_row.pack(anchor=W, pady=(0, Theme.PAD_SM))

        RoundedButton(btn_row, text="Select Folder",
                      command=callbacks['batch_process_folder'],
                      variant="warning", width=140, height=34).grid(row=0, column=0, padx=(0, 8))
        RoundedButton(btn_row, text="Current Folder",
                      command=callbacks['batch_process_current'],
                      variant="secondary", width=140, height=34).grid(row=0, column=1, padx=(0, 8))

        clear_holder = tk.Frame(btn_row, bg=Theme.get("surface"))
        clear_holder.grid(row=0, column=2)

        # Progress bar (slim, custom coloured)
        prog_frame = tk.Frame(top, bg=Theme.get("progress_bg"), height=4)
        prog_frame.pack(fill=X, pady=(Theme.PAD_SM, 0))
        prog_frame.pack_propagate(False)

        batch_progress = ttk.Progressbar(prog_frame, bootstyle="success-striped",
                                         mode='determinate')
        batch_progress.pack(fill=X)

        bottom = _card(tab, bg_key="surface", pad=Theme.PAD_MD)
        bottom.grid(row=1, column=0, sticky=NSEW,
                    padx=Theme.PAD_LG, pady=Theme.PAD_SM)
        bottom.rowconfigure(2, weight=1)
        bottom.columnconfigure(0, weight=1)

        res_header = tk.Frame(bottom, bg=Theme.get("surface"))
        res_header.grid(row=0, column=0, sticky=EW)
        res_header.columnconfigure(0, weight=1)

        tk.Label(res_header, text="Batch Results", font=Theme.FONT_HEADING,
                 fg=Theme.get("text"), bg=Theme.get("surface")).grid(row=0, column=0, sticky=W)

        batch_count_label = tk.Label(res_header, text="", font=Theme.FONT_SMALL,
                                     fg=Theme.get("text_muted"), bg=Theme.get("surface"))
        batch_count_label.grid(row=0, column=1, sticky=E)

        _divider(bottom).grid(row=1, column=0, sticky=EW, pady=(Theme.PAD_XS, Theme.PAD_SM))

        batch_result_text = ThemedText(bottom)
        batch_result_text.grid(row=2, column=0, sticky=NSEW)

        RoundedButton(clear_holder, text="Clear",
                      command=lambda: batch_result_text.delete('1.0', END),
                      variant="secondary", width=100, height=34).pack()

        return {
            'batch_result_text': batch_result_text,
            'batch_count_label': batch_count_label,
            'batch_progress':    batch_progress,
        }

    # ------------------------------------------------------------------ #
    #  Tools
    # ------------------------------------------------------------------ #
    @staticmethod
    def create_tools_tab(notebook, callbacks):
        bg = Theme.get("bg")
        tab = tk.Frame(notebook, bg=bg)
        notebook.add(tab, text="  Tools  ")

        tab.columnconfigure(0, weight=1)

        # ---- External resources ----
        res_card = _card(tab, bg_key="surface", pad=Theme.PAD_LG)
        res_card.grid(row=0, column=0, sticky=EW, padx=Theme.PAD_LG, pady=(Theme.PAD_LG, 0))

        SectionHeader(res_card, title="External Resources").pack(anchor=W, pady=(0, Theme.PAD_MD))
        _divider(res_card).pack(fill=X, pady=(0, Theme.PAD_MD))

        links = [
            ("EOSInfo (Recommended)",
             "Windows utility for reliable Canon shutter count reading",
             "http://www.astrojargon.net/eosinfo.aspx"),
            ("Canon EOS Utility",
             "Official Canon camera management software",
             "https://www.canon-europe.com/support/consumer/products/cameras/"),
            ("ExifTool by Phil Harvey",
             "Professional command-line metadata extraction tool",
             "https://exiftool.org/"),
        ]
        for title, desc, url in links:
            TabFactory._link_row(res_card, title, desc, url)

        # ---- System information ----
        sys_card = _card(tab, bg_key="surface", pad=Theme.PAD_LG)
        sys_card.grid(row=1, column=0, sticky=EW, padx=Theme.PAD_LG, pady=Theme.PAD_SM)
        sys_card.columnconfigure(0, weight=1)

        SectionHeader(sys_card, title="System Information").pack(anchor=W, pady=(0, Theme.PAD_MD))
        _divider(sys_card).pack(fill=X, pady=(0, Theme.PAD_MD))

        RoundedButton(sys_card, text="Check Dependencies",
                      command=callbacks['check_dependencies'],
                      variant="primary", width=180, height=34).pack(anchor=W, pady=(0, Theme.PAD_SM))

        dependency_frame = tk.Frame(sys_card, bg=Theme.get("surface"))
        dependency_frame.pack(fill=X, anchor=W)

        return {'dependency_frame': dependency_frame}

    @staticmethod
    def _link_row(parent, title, description, url):
        """One link entry row."""
        row = tk.Frame(parent, bg=Theme.get("surface2"),
                       padx=Theme.PAD_MD, pady=Theme.PAD_SM)
        row.pack(fill=X, pady=(0, 6))
        row.columnconfigure(0, weight=1)

        # left accent stripe
        tk.Frame(row, width=3, bg=Theme.get("accent")).pack(side=LEFT, fill=Y, padx=(0, Theme.PAD_SM))

        text_col = tk.Frame(row, bg=Theme.get("surface2"))
        text_col.pack(side=LEFT, fill=X, expand=YES)

        tk.Label(text_col, text=title, font=Theme.FONT_HEADING,
                 fg=Theme.get("text"), bg=Theme.get("surface2")).pack(anchor=W)
        tk.Label(text_col, text=description, font=Theme.FONT_SMALL,
                 fg=Theme.get("text_muted"), bg=Theme.get("surface2")).pack(anchor=W, pady=(2, 0))

        RoundedButton(row, text="Open",
                      command=lambda u=url: webbrowser.open(u),
                      variant="ghost", width=90, height=30).pack(side=RIGHT, padx=(Theme.PAD_SM, 0))

    # ------------------------------------------------------------------ #
    #  Info / About
    # ------------------------------------------------------------------ #
    @staticmethod
    def create_info_tab(notebook, logo_image):
        bg = Theme.get("bg")
        tab = tk.Frame(notebook, bg=bg)
        notebook.add(tab, text="   Info   ")

        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)

        # scrollable canvas
        sb = tk.Scrollbar(tab, orient=VERTICAL, bg=Theme.get("surface2"),
                          troughcolor=Theme.get("bg"), bd=0, width=12)
        sb.grid(row=0, column=1, sticky=NS)

        canvas = tk.Canvas(tab, bg=bg, highlightthickness=0, yscrollcommand=sb.set)
        canvas.grid(row=0, column=0, sticky=NSEW)
        sb.config(command=canvas.yview)

        content = tk.Frame(canvas, bg=bg)
        win_id  = canvas.create_window((0, 0), window=content, anchor=NW)

        def _on_resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=e.width)

        content.bind("<Configure>", _on_resize)
        canvas.bind("<Configure>",  _on_resize)

        # bind mouse wheel
        def _scroll(e):
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _scroll)

        pad = Theme.PAD_LG
        center = _card(content, bg_key="surface", pad=40)
        center.pack(fill=X, padx=pad, pady=pad)

        if logo_image:
            tk.Label(center, image=logo_image, bg=Theme.get("surface")).pack(pady=(0, Theme.PAD_MD))

        tk.Label(center, text="Canon Shutter Counter Pro",
                 font=("Segoe UI", 28, "bold"),
                 fg=Theme.get("accent"),  bg=Theme.get("surface")).pack(pady=(0, 4))
        tk.Label(center, text="v2.0  ·  Professional Edition",
                 font=Theme.FONT_SMALL,
                 fg=Theme.get("text_muted"), bg=Theme.get("surface")).pack(pady=(0, pad))

        _divider(center).pack(fill=X, pady=(0, pad))

        info_sections = [
            ("Supported Cameras",
             "Canon EOS R1  ·  R3  ·  R5  ·  R5 II  ·  R6  ·  R6 II  ·  R6 III  ·  R8  ·  RP",
             "info"),
            ("Features",
             "CR3 file metadata extraction  ·  USB camera detection  ·  Batch folder processing  ·  Model-specific shutter ratings  ·  Dark / Light mode",
             "success"),
            ("Requirements",
             "Python 3.8+  ·  ExifTool  ·  PyWin32 (Windows)  ·  ttkbootstrap",
             "warning"),
            ("Important Note",
             "Canon R-series cameras typically do not store shutter count in CR3 EXIF data. For accurate reading, use USB connection with EOSInfo or Canon EOS Utility.",
             "danger"),
        ]

        for sec_title, sec_text, variant in info_sections:
            color_map = {
                "info":    Theme.get("info"),
                "success": Theme.get("success"),
                "warning": Theme.get("warning"),
                "danger":  Theme.get("danger"),
            }
            accent = color_map[variant]
            sec = tk.Frame(center, bg=Theme.get("surface2"), padx=Theme.PAD_MD, pady=Theme.PAD_MD)
            sec.pack(fill=X, pady=(0, Theme.PAD_SM))
            tk.Frame(sec, width=3, bg=accent).pack(side=LEFT, fill=Y, padx=(0, Theme.PAD_SM))
            inner = tk.Frame(sec, bg=Theme.get("surface2"))
            inner.pack(side=LEFT, fill=X, expand=YES)
            tk.Label(inner, text=sec_title, font=Theme.FONT_HEADING,
                     fg=Theme.get("text"), bg=Theme.get("surface2")).pack(anchor=W)
            tk.Label(inner, text=sec_text, font=Theme.FONT_SMALL,
                     fg=Theme.get("text_muted"), bg=Theme.get("surface2"),
                     wraplength=700, justify=LEFT).pack(anchor=W, pady=(4, 0))

        _divider(center).pack(fill=X, pady=pad)

        # Credits
        tk.Label(center, text="Credits & Attribution", font=Theme.FONT_TITLE,
                 fg=Theme.get("text"), bg=Theme.get("surface")).pack(anchor=W, pady=(0, Theme.PAD_SM))

        cred_items = [
            ("Developer",  "Noel Wangler – NoW Photography",    "https://noelwangler.ch"),
            ("ExifTool",   "Phil Harvey",                        "https://exiftool.org/"),
            ("ttkbootstrap","Israel Dryer",                      "https://ttkbootstrap.readthedocs.io/"),
            ("PyWin32",    "Mark Hammond",                       None),
            ("Python",     "Python Software Foundation",         "https://python.org"),
        ]
        for role, name, link in cred_items:
            row = tk.Frame(center, bg=Theme.get("surface"))
            row.pack(fill=X, pady=2)
            tk.Label(row, text=f"{role}:", font=Theme.FONT_SMALL,
                     fg=Theme.get("text_muted"), bg=Theme.get("surface"),
                     width=14, anchor=W).pack(side=LEFT)
            lbl = tk.Label(row, text=name,
                           font=Theme.FONT_SMALL if not link else (Theme.FONT_SMALL[0], Theme.FONT_SMALL[1], "underline"),
                           fg=Theme.get("accent") if link else Theme.get("text"),
                           bg=Theme.get("surface"),
                           cursor="hand2" if link else "")
            lbl.pack(side=LEFT)
            if link:
                lbl.bind("<Button-1>", lambda e, u=link: webbrowser.open(u))


# ---------------------------------------------------------------------------
# Dependency row widget
# ---------------------------------------------------------------------------

class DependencyRowWidget:
    """Widget for displaying dependency check results."""

    @staticmethod
    def create(parent, name, value, status):
        color = Theme.get("success") if status else Theme.get("danger")
        row = tk.Frame(parent, bg=Theme.get("surface2"),
                       padx=Theme.PAD_SM, pady=Theme.PAD_SM)
        row.pack(fill=X, pady=(0, 4))

        # coloured dot
        tk.Frame(row, width=8, height=8, bg=color).pack(side=LEFT, padx=(0, Theme.PAD_SM), pady=5)

        tk.Label(row, text=f"{name}:", font=Theme.FONT_HEADING,
                 fg=Theme.get("text"), bg=Theme.get("surface2")).pack(side=LEFT)

        tk.Label(row, text=value, font=Theme.FONT_BODY,
                 fg=Theme.get("text_muted"), bg=Theme.get("surface2")).pack(side=LEFT, padx=8)

        tag = "OK" if status else "FAIL"
        tag_color = Theme.get("success") if status else Theme.get("danger")
        tk.Label(row, text=f"[{tag}]", font=Theme.FONT_SMALL,
                 fg=tag_color, bg=Theme.get("surface2")).pack(side=RIGHT)

        return row

