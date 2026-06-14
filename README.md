# EasyHotCorners

<img src="icon.svg" width="64" height="64" align="right" alt="EasyHotCorners icon"/>

A lightweight, modular hot corner manager for Windows 11. Assign actions to any corner of your screen and trigger them by moving your mouse to that corner, with animated feedback and full per-corner customization.

---

## Features

- **Four independent hot corners** — Top Left, Top Right, Bottom Left, Bottom Right, each fully configurable.
- **Animated overlay** — Four distinct animation styles rendered at up to 60 fps: Arc, Corner Bar, Pulse, and Fade Box.
- **Custom animation color** — Choose any color per corner via a built-in color picker.
- **Configurable delay** — Set how long the mouse must dwell in a corner before the action fires (0.1 s – 5.0 s).
- **System Tray integration** — The application lives in the Windows system tray. No persistent window is shown while idle.
- **Desktop-only activation** — Hot corners are suppressed when a fullscreen or maximized application is in the foreground, preventing accidental triggers.
- **Built-in actions:**
  - Toggle desktop icons (show / hide)
  - Lock screen
  - Show desktop (Win + D)
  - Mute / unmute system volume
- **Custom Python scripts** — Drop any `.py` file into the scripts folder and it will appear as a selectable action inside the settings window.
- **Extensible API** — An `easy_api.py` file is provided in the scripts folder as a reusable helper base you can import from your own scripts.
- **Theme support** — Dark, Light, or automatic System theme (reads the Windows registry).
- **Language support** — English and Spanish, selectable from the settings window.

---

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or later
- The packages listed in `requirements.txt`

Install dependencies:

```
pip install -r requirements.txt
```

---

## Running from Source

```
python main.py
```

The application starts silently in the system tray. Right-click the tray icon to open Settings or quit.

---

## Building a Standalone Executable

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```
2. Run the build command (also available in `export.txt`):
   ```
   pyinstaller --noconfirm --onefile --windowed --icon="icon.ico" --name="EasyHotCorners" --add-data "icon.ico;." main.py
   ```
3. The finished executable will be at `dist/EasyHotCorners.exe`.

---

## Configuration

All settings are stored in `%APPDATA%\EasyHotCorners\settings.json` and are edited through the graphical settings window. No manual JSON editing is required.

| Setting   | Description                                         |
| --------- | --------------------------------------------------- |
| Language  | Interface language (English or Spanish).            |
| Theme     | Color scheme: System (auto-detect), Dark, or Light. |
| Enable    | Toggle a corner on or off individually.             |
| Action    | Built-in action or custom script to execute.        |
| Animation | Visual style shown while dwelling in the corner.    |
| Color     | Color of the animation overlay.                     |
| Delay     | Dwell time in seconds before the action fires.      |

---

## Custom Scripts

Place any `.py` file in `%APPDATA%\EasyHotCorners\scripts\`. It will appear automatically as a selectable action in the settings window. Scripts are executed in a new process using the same Python interpreter that runs the application.

An `easy_api.py` helper file is generated in the same scripts folder on first launch. It can be imported from your own scripts and edited freely.

Example structure:

```
%APPDATA%\EasyHotCorners\
    settings.json
    scripts\
        easy_api.py
        my_custom_action.py
```

---

## Project Structure

| File               | Purpose                                                     |
| ------------------ | ----------------------------------------------------------- |
| `main.py`          | Application entry point, system tray, theme management.     |
| `engine.py`        | Mouse position polling at ~60 Hz, corner detection signals. |
| `overlay_ui.py`    | Transparent overlay window, animation rendering.            |
| `settings_ui.py`   | Configuration window built with PySide6.                    |
| `config.py`        | Settings persistence (`%APPDATA%\EasyHotCorners`).          |
| `actions.py`       | Built-in action definitions and script execution.           |
| `i18n.py`          | English and Spanish translation strings.                    |
| `icon.svg`         | Application icon (source format).                           |
| `export.txt`       | PyInstaller build command reference.                        |
| `requirements.txt` | Python dependency list.                                     |

---

## License

MIT
