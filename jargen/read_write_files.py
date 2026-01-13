from yaml import safe_load, YAMLError
from typing import Any


def read_yaml(path: str) -> dict[str, Any]:
    try:
        with open(path) as file:
            content = safe_load(file)
    except FileNotFoundError as e:
        print(f"Configuration file not found at path: {e.filename}")
        exit(-1)
    except YAMLError as e:
        print(f"YAML Syntax Error:\n{e}")
        exit(-1)

    return content
