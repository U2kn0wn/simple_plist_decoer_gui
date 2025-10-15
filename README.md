# plist-viewer

A small, drag-and-drop friendly GUI for decoding Apple `.plist` files (XML & binary) into readable JSON on Linux. Built with `tkinter` and optional drag-and-drop support via `tkinterdnd2`. Designed for simplicity: open files from the dialog, or drop them onto the app (when running under X11 and `tkinterdnd2` is installed).

---

## Features

- Decode XML and binary `.plist` using Python's `plistlib`
    
- Pretty-print decoded content as JSON
    
- Show raw file contents if decoding fails
    
- Open files via **Open…** or by dragging files onto the app (requires `tkinterdnd2` + X11)
    
- Save decoded JSON or copy it to the clipboard
    
- Small, single-file script: `plist_viewer.py`
    

---

## Requirements

- Python 3.8+
    
- `tkinter` (system package `python3-tk`)
    
- (Optional, for drag & drop) `tkinterdnd2` Python package
    
- X11 session for drag & drop (Wayland may not forward drops to tkinter apps)
    

---

## Installation (Ubuntu)

Open a terminal and run:

`sudo apt update sudo apt install -y python3 python3-tk python3-pip pip3 install --user tkinterdnd2`

Notes:

- Installing `tkinterdnd2` is optional; the app will run without it but drag-and-drop is disabled.
    
- If you installed `tkinterdnd2` and drag-and-drop still doesn't work, make sure you're running an **X11** session (see Troubleshooting).
    

---

## Usage

1. Save the script to a file, for example:
    
    `/home/you/tools/plist_viewer.py`
    
2. Make it executable:
    
    `chmod +x /home/you/tools/plist_viewer.py`
    
3. Run it:
    
    `/usr/bin/python3 /home/you/tools/plist_viewer.py`
    
    or
    
    `./plist_viewer.py /path/to/some.plist`
    

- **Open…** button works regardless of drag support.
    
- To drop files onto the app window, ensure `tkinterdnd2` is installed and you are on an X11 session.
    

---

## Make a Desktop Launcher (so you can drop files onto the icon)

Replace `/full/path/to/plist_viewer.py` with the absolute path to your script.

`mkdir -p ~/.local/share/applications  cat > ~/.local/share/applications/plist-viewer.desktop <<'EOF' [Desktop Entry] Name=Plist Viewer Comment=Decode and view plist files Exec=/usr/bin/python3 /full/path/to/plist_viewer.py %F Icon=utilities-terminal Terminal=false Type=Application Categories=Utility; MimeType=application/x-plist;text/plain; EOF  chmod +x ~/.local/share/applications/plist-viewer.desktop  # optional: copy to Desktop so you can drag files onto it cp ~/.local/share/applications/plist-viewer.desktop ~/Desktop/ chmod +x ~/Desktop/plist-viewer.desktop # On GNOME: right-click the Desktop icon -> Allow Launching`

`%F` allows the launcher to accept multiple dropped files.

---

## X11 vs Wayland — important

- `tkinterdnd2` and many tkinter DnD integrations expect X11 (Xorg). Under Wayland, drag-and-drop may not work or will behave inconsistently.
    
- If drag-and-drop doesn't work at all despite `tkinterdnd2` being installed, log out and choose **Ubuntu on Xorg** / **X11** session from your display manager, then log back in and try again.
    

---

## Quick troubleshooting

- **App opens but dropping does nothing**
    
    - Confirm `tkinterdnd2` installed:
        
        `python3 -c "import tkinterdnd2; print('ok')"`
        
        If that raises `ModuleNotFoundError`, run `pip3 install --user tkinterdnd2`.
        
    - Confirm you are in an X11 session (not Wayland).
        
    - Check the status bar — if it says `Drag-and-drop unavailable`, the DnD module isn't present.
        
- **Script won’t run by double-click**
    
    - Make sure it’s executable (`chmod +x ...`) and the shebang is `#!/usr/bin/env python3`.
        
    - Desktop environments sometimes refuse to run arbitrary scripts; use the `.desktop` launcher described above.
        
- **What the desktop actually passes**
    
    - Use a wrapper to log arguments:
        
        `cat > ~/plist_wrapper.sh <<'EOF' #!/usr/bin/env bash echo "$(date) ARGS: $@" >> /tmp/plist_args.log /usr/bin/python3 /full/path/to/plist_viewer.py "$@" EOF chmod +x ~/plist_wrapper.sh`
        
        Change the `.desktop` to call the wrapper and inspect `/tmp/plist_args.log` after a drop.
        
- **File path encoding**  
    The script handles `file://` URIs and space-encoded paths (`%20`) and also cleans braces some file managers add.
    

---

## Behavior & UI summary

- Left pane: list of opened files
    
- Right pane: preview (Decoded JSON or raw text)
    
- Toolbar:
    
    - **Open…**: open selected plist(s)
        
    - **Save JSON**: save decoded data
        
    - **Copy JSON**: copy decoded JSON to clipboard
        
    - Radio buttons: switch between Decoded and Raw view
        
- Status bar: shows file path and DnD availability
    

---

## Example workflows

- Double-click a `.plist` file to open with **Open With** → _Plist Viewer_ (register with the `.desktop` file).
    
- Drag one or multiple `.plist` files onto the Desktop launcher icon (or dock icon if pinned) to open them in the viewer.
    
- Use the **Save JSON** button to export decoded files for automated processing.
    

---

## Development / Improvements

Possible future additions:

- Syntax highlighting for JSON (e.g., `tkinter.scrolledtext` + `ttk` styles or use a text widget highlighter)
    
- Batch export of multiple plists to a single JSON file
    
- Auto-detection / pretty formatting of timestamps or binary plist special types
    
- Integration test to verify DnD behavior across desktop environments
    

---

## Security & privacy note

This tool only reads files you explicitly open or drop. No network activity or telemetry. However, be mindful opening plist files from untrusted sources — they may contain arbitrary strings. The app does not execute any code contained in .plist data.
