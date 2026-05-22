"""Small launcher EXE entry: starts desktop pet without console (icon embedded in EXE)."""

import os
import subprocess
import sys


def _root() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    root = _root()
    pyw = os.path.join(root, ".venv", "Scripts", "pythonw.exe")
    if not os.path.isfile(pyw):
        pyw = "pythonw"
    main_py = os.path.join(root, "main.py")
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen([pyw, main_py], cwd=root, creationflags=flags)


if __name__ == "__main__":
    main()
