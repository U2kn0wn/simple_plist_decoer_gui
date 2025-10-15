#!/usr/bin/env python3
import sys
import json
import os
import plistlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font

APP_TITLE = "plist viewer"

# --- Drag & Drop support -----------------------------------------------
# We try to import tkinterdnd2; if missing, the app still runs (without DnD).
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_OK = True
except Exception:
    DND_OK = False
    DND_FILES = None
    TkinterDnD = None

def _normalize_dropped_paths(tk_root, data):
    """
    data is a tk 'list' string; use tk.splitlist to handle spaces/braces.
    Items may look like '/path/file.plist' or 'file:///path/file.plist'
    """
    items = tk_root.tk.splitlist(data)
    paths = []
    for it in items:
        # Strip file:// if present
        if it.startswith("file://"):
            # On Linux file:// URIs, spaces are %-encoded
            it = it[7:]
            it = it.replace("%20", " ")
        # Remove surrounding braces that some FMs add for spaced paths
        if it.startswith("{") and it.endswith("}"):
            it = it[1:-1]
        paths.append(it)
    # Filter only existing files (and optionally .plist files)
    return [p for p in paths if os.path.isfile(p)]

# --- Core logic ---------------------------------------------------------
def load_plist(path):
    try:
        with open(path, "rb") as f:
            data = plistlib.load(f)
        return ("decoded", data)
    except Exception as e:
        try:
            with open(path, "rb") as f:
                raw = f.read().decode("utf-8", "replace")
            return ("raw", raw, str(e))
        except Exception as e2:
            return ("error", f"Unable to read file: {e2}")

# Choose Tk class depending on DnD availability
_BaseTk = TkinterDnD.Tk if DND_OK else tk.Tk

class PlistViewer(_BaseTk):
    def __init__(self, initial_files=None):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1000x600")
        self.minsize(600, 400)

        self.files = list(initial_files or [])
        self.current_index = None

        self._build_ui()
        self._wire_dnd()

        if self.files:
            self.populate_list(self.files)
            self.file_list.selection_set(0)
            self.on_select(None)

    def _build_ui(self):
        # top toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(side="top", fill="x", padx=6, pady=6)

        btn_open = ttk.Button(toolbar, text="Open...", command=self.open_file)
        btn_open.pack(side="left")

        btn_save = ttk.Button(toolbar, text="Save JSON", command=self.save_json)
        btn_save.pack(side="left", padx=6)

        btn_copy = ttk.Button(toolbar, text="Copy JSON", command=self.copy_json)
        btn_copy.pack(side="left")

        self.toggle_var = tk.StringVar(value="decoded")
        ttk.Radiobutton(toolbar, text="Decoded", variable=self.toggle_var, value="decoded", command=self.update_view).pack(side="right")
        ttk.Radiobutton(toolbar, text="Raw", variable=self.toggle_var, value="raw", command=self.update_view).pack(side="right")

        # main panes
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left = ttk.Frame(paned, width=240)
        paned.add(left, weight=1)

        right = ttk.Frame(paned)
        paned.add(right, weight=4)

        # file list
        lbl_files = ttk.Label(left, text="Files")
        lbl_files.pack(anchor="w", padx=6, pady=(6,0))

        self.file_list = tk.Listbox(left, exportselection=False)
        self.file_list.pack(fill="both", expand=True, padx=6, pady=6)
        self.file_list.bind("<<ListboxSelect>>", self.on_select)

        # content display
        lbl_preview = ttk.Label(right, text="Preview")
        lbl_preview.pack(anchor="w", padx=6, pady=(6,0))

        text_frame = ttk.Frame(right)
        text_frame.pack(fill="both", expand=True, padx=6, pady=6)

        self.text = tk.Text(text_frame, wrap="none")
        self.text.pack(side="left", fill="both", expand=True)

        mono = font.nametofont("TkFixedFont")
        self.text.configure(font=mono)

        # scrollbars
        ysb = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        ysb.pack(side="right", fill="y")
        self.text.configure(yscrollcommand=ysb.set)

        xsb = ttk.Scrollbar(right, orient="horizontal", command=self.text.xview)
        xsb.pack(fill="x")
        self.text.configure(xscrollcommand=xsb.set)

        # status bar
        self.status = ttk.Label(self, text="", anchor="w")
        self.status.pack(side="bottom", fill="x")

        if not DND_OK:
            self.status.config(text="Drag-and-drop unavailable: install 'tkinterdnd2' to enable dropping files.")

    def _wire_dnd(self):
        if not DND_OK:
            return
        # Allow dropping files on the whole window, listbox, and text area
        for widget in (self, self.file_list, self.text):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop_files)

    def _on_drop_files(self, event):
        paths = _normalize_dropped_paths(self, event.data)
        if not paths:
            return
        # Append to current list (or replace? choose append here)
        self.populate_list(self.files + paths if self.files else paths)
        self.file_list.selection_clear(0, "end")
        self.file_list.selection_set("end")
        self.on_select(None)

    def populate_list(self, paths):
        self.file_list.delete(0, "end")
        self.files = list(paths)
        for p in self.files:
            self.file_list.insert("end", p)

    def open_file(self):
        paths = filedialog.askopenfilenames(title="Open plist(s)", filetypes=[("plist files","*.plist *.PLIST *.*")])
        if not paths:
            return
        self.populate_list(paths)
        self.file_list.selection_set(0)
        self.on_select(None)

    def on_select(self, event):
        sel = self.file_list.curselection()
        if not sel:
            return
        idx = sel[0]
        self.current_index = idx
        path = self.files[idx]
        result = load_plist(path)
        if result[0] == "decoded":
            self.decoded_json = json.dumps(result[1], indent=2, ensure_ascii=False)
            self.raw_text = None
            self.status.config(text=f"Decoded: {path}")
            self.toggle_var.set("decoded")
        elif result[0] == "raw":
            self.decoded_json = None
            self.raw_text = result[1]
            self.status.config(text=f"Raw (decoded failed): {path} — error: {result[2]}")
            self.toggle_var.set("raw")
        else:
            self.decoded_json = None
            self.raw_text = str(result)
            self.status.config(text=f"Error reading file: {path}")
            self.toggle_var.set("raw")
        self.update_view()

    def update_view(self):
        self.text.delete("1.0", "end")
        mode = self.toggle_var.get()
        if mode == "decoded":
            if getattr(self, "decoded_json", None) is not None:
                self.text.insert("1.0", self.decoded_json)
            else:
                self.text.insert("1.0", "(no decoded JSON available)")
        else:
            if getattr(self, "raw_text", None) is not None:
                self.text.insert("1.0", self.raw_text)
            else:
                self.text.insert("1.0", "(no raw text available)")

    def save_json(self):
        if not getattr(self, "decoded_json", None):
            messagebox.showinfo("Save JSON", "No decoded JSON available for current file.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.decoded_json)
        messagebox.showinfo("Saved", f"Saved JSON to: {path}")

    def copy_json(self):
        if not getattr(self, "decoded_json", None):
            messagebox.showinfo("Copy JSON", "No decoded JSON available for current file.")
            return
        self.clipboard_clear()
        self.clipboard_append(self.decoded_json)
        messagebox.showinfo("Copied", "Decoded JSON copied to clipboard")

def main():
    args = sys.argv[1:]
    app = PlistViewer(initial_files=args)
    app.mainloop()

if __name__ == "__main__":
    main()

