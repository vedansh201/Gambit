import json
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent / "settings.json"

def get_default_settings():
    return {
        "genre":"",
        "last_changed_date":"",
        "used_wallpaper_ids": [],
        "wallpaper_folder": str(Path.home()  / "Pictures" / "Gambit"),
    }


def load_settings():
    if not SETTINGS_FILE.exists():
        return get_default_settings()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return get_default_settings()

    if not isinstance(data, dict):
        return get_default_settings()
    
    defaults = get_default_settings()       



    for key, value in defaults.items():
        if key not in data:
            data[key] = value

    if not isinstance(data["used_wallpaper_ids"], list):
        data["used_wallpaer_ids"] = []

    if not isinstance(data["wallpaper_folder"], str):
        data["wallpaper_folder"] = defaults["wallpaper_folder"]

    return data

def save_settings(data):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

            return True
    except OSError:
        return False
