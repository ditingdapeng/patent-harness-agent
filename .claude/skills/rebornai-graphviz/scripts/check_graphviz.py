from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from typing import Iterable


def install_commands(system_name: str) -> Iterable[str]:
    if system_name == "Windows":
        return (
            "winget install Graphviz.Graphviz",
            "choco install graphviz",
            "scoop install graphviz",
        )
    if system_name == "Darwin":
        return ("brew install graphviz",)
    return (
        "sudo apt-get update && sudo apt-get install -y graphviz",
        "sudo dnf install -y graphviz",
        "sudo yum install -y graphviz",
        "sudo pacman -S graphviz",
        "sudo zypper install graphviz",
    )


def main() -> int:
    system_name = platform.system() or "Unknown"
    dot_path = shutil.which("dot")

    print(f"platform={system_name}")

    if not dot_path:
        print("status=missing")
        print("message=Graphviz dot command was not found in PATH.")
        print("install_commands=")
        for command in install_commands(system_name):
            print(f"  - {command}")
        print("verify_command=dot -V")
        return 1

    completed = subprocess.run(
        [dot_path, "-V"],
        capture_output=True,
        text=True,
        check=False,
    )
    version_text = (completed.stderr or completed.stdout or "").strip()

    print("status=installed")
    print(f"dot_path={dot_path}")
    print(f"version={version_text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
