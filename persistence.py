import json
import os
from datetime import datetime

SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "blue",
    "difficulty": "normal"
}


def ensure_json_file(path, default_value):
    """
    Create JSON file if it does not exist.
    """
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(default_value, file, indent=4)


def load_settings():
    """
    Load settings from file.
    If file is missing or broken, return defaults.
    """
    ensure_json_file(SETTINGS_FILE, DEFAULT_SETTINGS)

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Make sure all required keys exist
        for key, value in DEFAULT_SETTINGS.items():
            if key not in data:
                data[key] = value

        return data
    except:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """
    Save settings to JSON.
    """
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def load_leaderboard():
    """
    Load leaderboard from JSON.
    """
    ensure_json_file(LEADERBOARD_FILE, [])

    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        return data
    except:
        return []


def save_leaderboard(rows):
    """
    Save leaderboard rows to JSON.
    """
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as file:
        json.dump(rows, file, indent=4)


def add_score(name, score, distance, coins):
    """
    Add one score entry, keep only top 10.
    """
    leaderboard = load_leaderboard()

    leaderboard.append({
        "name": name,
        "score": score,
        "distance": distance,
        "coins": coins,
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    leaderboard.sort(
        key=lambda row: (row["score"], row["distance"], row["coins"]),
        reverse=True
    )

    leaderboard = leaderboard[:10]
    save_leaderboard(leaderboard)