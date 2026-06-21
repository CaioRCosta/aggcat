import json
from pathlib import Path

CONFIG_FILE_NAME = ".aggcat.json"


def get_config_path() -> Path:
    return Path.cwd() / CONFIG_FILE_NAME


def load_config() -> dict:
    path = get_config_path()
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config: dict) -> None:
    path = get_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def reset_config() -> None:
    path = get_config_path()
    if path.exists():
        path.unlink()