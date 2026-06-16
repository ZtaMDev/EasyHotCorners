import os
import json
import shutil
import winreg

APP_NAME = "EasyHotCorners"
APPDATA_DIR = os.path.join(os.environ.get('APPDATA', ''), APP_NAME)
SETTINGS_FILE = os.path.join(APPDATA_DIR, "settings.json")
SCRIPTS_DIR = os.path.join(APPDATA_DIR, "scripts")
PROFILES_DIR = os.path.join(APPDATA_DIR, "profiles")

DEFAULT_SETTINGS = {
    "language": "en",
    "theme": "system",
    "radius": 10,
    "multi_monitor": True,
    "polling_interval": 16,
    "block_any_maximized": True,
    "current_profile": "Default",
    "corners": {
        "TOP_LEFT": {"enabled": True, "action_id": "toggle_desktop_icons", "delay": 0.4, "animation": "pulse", "color": "#ffffff", "allow_maximized": False},
        "TOP_RIGHT": {"enabled": False, "action_id": "none", "delay": 0.4, "animation": "pulse", "color": "#ffffff", "allow_maximized": True},
        "BOTTOM_LEFT": {"enabled": False, "action_id": "none", "delay": 0.4, "animation": "pulse", "color": "#ffffff", "allow_maximized": True},
        "BOTTOM_RIGHT": {"enabled": False, "action_id": "none", "delay": 0.4, "animation": "pulse", "color": "#ffffff", "allow_maximized": True}
    }
}

def is_dark_mode():
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except Exception:
        return False

def effective_is_dark(settings):
    theme = settings.get("theme", "system")
    if theme == "system":
        return is_dark_mode()
    return theme == "dark"

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

    # Migrate default profile if needed
    _init_profiles()

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
                    if "switch_profile" not in settings['corners'][corner]:
                        settings['corners'][corner]["switch_profile"] = ""
                        modified = True
            # Load profile data on top (profile settings override)
            profile_name = settings.get("current_profile", "Default")
            profile_data = load_profile(profile_name)
            if profile_data is not None:
                for k, v in profile_data.items():
                    settings[k] = v
                settings["current_profile"] = profile_name
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


# ─────────────────────────────────────────────
# Profiles
# ─────────────────────────────────────────────

def _init_profiles():
    """Ensure profiles dir exists and migrate Default profile."""
    os.makedirs(PROFILES_DIR, exist_ok=True)
    default_path = os.path.join(PROFILES_DIR, "Default.json")
    if not os.path.exists(default_path):
        # Create Default profile from current settings (strip profile key)
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except Exception:
            settings = {}
        copy = dict(settings)
        copy.pop("current_profile", None)
        with open(default_path, 'w', encoding='utf-8') as f:
            json.dump(copy, f, indent=4)


def list_profiles():
    """Return sorted list of profile names (without .json)."""
    os.makedirs(PROFILES_DIR, exist_ok=True)
    names = []
    for fname in os.listdir(PROFILES_DIR):
        if fname.endswith(".json"):
            names.append(fname[:-5])
    return sorted(names) if names else ["Default"]


def load_profile(name):
    """Load a profile by name, returns a settings dict (without current_profile)."""
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_profile(name, data):
    """Save a settings dict as a profile."""
    os.makedirs(PROFILES_DIR, exist_ok=True)
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    # Update settings.json current_profile
    settings = {}
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except Exception:
        pass
    settings["current_profile"] = name
    save_settings(settings)


def delete_profile(name):
    """Delete a profile by name. Cannot delete the last profile."""
    profiles = list_profiles()
    if len(profiles) <= 1:
        return False
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
    # If current profile was deleted, switch to first available
    settings = {}
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except Exception:
        pass
    current = settings.get("current_profile", "Default")
    if current == name or not os.path.exists(os.path.join(PROFILES_DIR, f"{current}.json")):
        remaining = list_profiles()
        if remaining:
            settings["current_profile"] = remaining[0]
            save_settings(settings)
    return True


def rename_profile(old_name, new_name):
    """Rename a profile."""
    if not new_name or old_name == new_name:
        return False
    old_path = os.path.join(PROFILES_DIR, f"{old_name}.json")
    new_path = os.path.join(PROFILES_DIR, f"{new_name}.json")
    if not os.path.exists(old_path) or os.path.exists(new_path):
        return False
    os.rename(old_path, new_path)
    # Update current_profile if needed
    settings = {}
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except Exception:
        pass
    if settings.get("current_profile") == old_name:
        settings["current_profile"] = new_name
        save_settings(settings)
    return True


def switch_profile(name):
    """Switch to a profile: save current corner settings, load the new profile into settings.json."""
    profile_data = load_profile(name)
    if profile_data is None:
        return False
    # Merge profile data over current settings (preserve app-level keys)
    settings = {}
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except Exception:
        settings = dict(DEFAULT_SETTINGS)
    # Save current settings into old profile before switching
    current_name = settings.get("current_profile", "Default")
    old_profile = dict(settings)
    old_profile.pop("current_profile", None)
    save_profile(current_name, old_profile)
    # Apply new profile
    for k, v in profile_data.items():
        settings[k] = v
    settings["current_profile"] = name
    save_settings(settings)
    return True


def export_profile(name, target_path):
    """Copy a profile JSON to an external path."""
    src = os.path.join(PROFILES_DIR, f"{name}.json")
    if not os.path.exists(src):
        return False
    shutil.copy2(src, target_path)
    return True


def import_profile(source_path):
    """Copy an external JSON into profiles dir. Returns profile name or None."""
    if not os.path.exists(source_path):
        return None
    base = os.path.splitext(os.path.basename(source_path))[0]
    name = base
    counter = 1
    while os.path.exists(os.path.join(PROFILES_DIR, f"{name}.json")):
        name = f"{base} ({counter})"
        counter += 1
    dst = os.path.join(PROFILES_DIR, f"{name}.json")
    shutil.copy2(source_path, dst)
    return name
