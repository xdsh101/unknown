import json
import os

SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"


def load_settings():
    default_settings = {
        "sound": True,
        "car_color": "blue",
        "difficulty": "normal"
    }

    if not os.path.exists(SETTINGS_FILE):
        save_settings(default_settings)
        return default_settings

    with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)
        return []

    with open(LEADERBOARD_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as file:
        json.dump(leaderboard, file, indent=4)


def add_score(name, score, distance):
    leaderboard = load_leaderboard()

    leaderboard.append({
        "name": name,
        "score": score,
        "distance": distance
    })

    leaderboard.sort(key=lambda row: row["score"], reverse=True)
    leaderboard = leaderboard[:10]
    save_leaderboard(leaderboard)