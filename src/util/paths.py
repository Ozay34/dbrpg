import os
import sys
from pathlib import Path


EXE = getattr(sys, 'frozen', False)


def resolve_path(path):
    if EXE:
        return Path(sys._MEIPASS) / path
    return Path.cwd() / path
