import os
from pathlib import Path
from typing import Union


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


def find_file(filename: Union[str, Path]):
    for root, _, files in os.walk(ROOT_DIR):
        if filename in files:
            return os.path.join(root, filename)
    raise FileNotFoundError("File not found!")
