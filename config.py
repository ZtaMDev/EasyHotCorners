import os
import json

APP_NAME = "EasyHotCorners"
APPDATA_DIR = os.path.join(os.environ.get('APPDATA', ''), APP_NAME)
SETTINGS_FILE = os.path.join(APPDATA_DIR, "settings.json")
SCRIPTS_DIR = os.path.join(APPDATA_DIR, "scripts")

DEFAULT_SETTINGS = {
    "language": "en",
    "theme": "system",
    "corners": {
        "TOP_LEFT": {"enabled": True, "action_id": "toggle_desktop_icons", "delay": 0.6, "animation": "pulse", "color": "#ffffff", "allow_maximized": False},
        "TOP_RIGHT": {"enabled": False, "action_id": "none", "delay": 0.6, "animation": "pulse", "color": "#ffffff", "allow_maximized": True},
        "BOTTOM_LEFT": {"enabled": False, "action_id": "none", "delay": 0.6, "animation": "pulse", "color": "#ffffff", "allow_maximized": True},
        "BOTTOM_RIGHT": {"enabled": False, "action_id": "none", "delay": 0.6, "animation": "pulse", "color": "#ffffff", "allow_maximized": True}
    }
}

def init_appdata():
    os.makedirs(APPDATA_DIR, exist_ok=True)
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    
    # Create default api file
    api_file = os.path.join(SCRIPTS_DIR, "easy_api.py")
    if not os.path.exists(api_file):
        with open(api_file, 'w', encoding='utf-8') as f:
            f.write('"""\nEasyHotCorners Custom API\nImport this in your custom scripts if needed.\n"""\n\n')
            f.write('def show_notification(title, message):\n')
            f.write('    print(f"[{title}] {message}")\n')

    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)

def load_settings():
    init_appdata()
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            modified = False
            # Merge with defaults
            for key, val in DEFAULT_SETTINGS.items():
                if key not in settings:
                    settings[key] = val
                    modified = True
            for corner, val in DEFAULT_SETTINGS['corners'].items():
                if corner not in settings['corners']:
                    settings['corners'][corner] = val
                    modified = True
                else:
                    if "animation" not in settings['corners'][corner]:
                        settings['corners'][corner]["animation"] = "pulse"
                        modified = True
                    if "color" not in settings['corners'][corner]:
                        settings['corners'][corner]["color"] = "#ffffff"
                        modified = True
                    if "allow_maximized" not in settings['corners'][corner]:
                        settings['corners'][corner]["allow_maximized"] = val.get("allow_maximized", False)
                        modified = True
            if modified:
                save_settings(settings)
            return settings
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    # Ensure init_appdata is not repeatedly calling save_settings
    os.makedirs(APPDATA_DIR, exist_ok=True)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)
