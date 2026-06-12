from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

MIN_DPI = 300


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a Graphviz DOT file to PNG with dpi >= 300.")
    parser.add_argument("--input", required=True, help="Path to the input .dot file")
    parser.add_argument("--output", help="Path to the output .png file")
    parser.add_argument("--dpi", type=int, default=MIN_DPI, help="Output DPI. Must be >= 300.")
    return parser.parse_args()


def infer_sibling_output_dir(root_dir: Path) -> Path:
    png_dir = root_dir / "png"
    images_dir = root_dir / "images"

    if png_dir.exists() and images_dir.exists():
        raise ValueError(
            "Both 'png' and 'images' directories exist beside the 'dot' directory. "
            "Pass --output explicitly to avoid mixing conventions."
        )
    if png_dir.exists():
        return png_dir
    return images_dir


def resolve_output_path(input_path: Path, output: str | None) -> Path:
    if output:
        return Path(output)
    if input_path.parent.name == "dot":
        output_dir = infer_sibling_output_dir(input_path.parent.parent)
        return output_dir / f"{input_path.stem}.png"
    raise ValueError("Output path is required unless the input file is inside a 'dot' directory.")


def ensure_graphviz() -> str:
    dot_path = shutil.which("dot")
    if not dot_path:
        raise RuntimeError("Graphviz dot command was not found in PATH. Run check_graphviz.py first.")
    return dot_path


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)

    if args.dpi < MIN_DPI:
        raise ValueError(f"DPI must be >= {MIN_DPI}, got {args.dpi}.")
    if not input_path.exists():
        raise FileNotFoundError(f"Input DOT file does not exist: {input_path}")
    if input_path.suffix.lower() != ".dot":
        raise ValueError(f"Input file must use the .dot extension: {input_path}")

    output_path = resolve_output_path(input_path, args.output)
    if output_path.suffix.lower() != ".png":
        raise ValueError(f"Output file must use the .png extension: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dot_path = ensure_graphviz()

    completed = subprocess.run(
        [dot_path, "-Tpng", f"-Gdpi={args.dpi}", str(input_path), "-o", str(output_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.returncode != 0:
        error_text = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(error_text or "Graphviz rendering failed.")

    print(f"input={input_path}")
    print(f"output={output_path}")
    print(f"dpi={args.dpi}")
    print("status=rendered")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"status=failed\nmessage={exc}")
        sys.exit(1)
