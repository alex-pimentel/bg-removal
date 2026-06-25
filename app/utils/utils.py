import os
import json
from typing import Optional

def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
    value = os.environ.get(var_name, default)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set")
    return value

def save_json_data(file_path: str, data: dict):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def load_json_data(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)