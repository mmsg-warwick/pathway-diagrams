"""Export draw.io files to PNG using the draw.io desktop application."""

import subprocess
from pathlib import Path

from pipeline.config import DRAWIO_EXECUTABLE


def export_to_png(drawio_path: Path, output_path: Path) -> None:
    """Export a draw.io file to a PNG by invoking the draw.io CLI.

    Raises:
        FileNotFoundError: if the draw.io executable or the source file is missing.
        subprocess.CalledProcessError: if draw.io exits with a non-zero status.
    """
    drawio_path = Path(drawio_path)
    output_path = Path(output_path)

    if not DRAWIO_EXECUTABLE.exists():
        raise FileNotFoundError(f"draw.io executable not found: {DRAWIO_EXECUTABLE}")

    if not drawio_path.exists():
        raise FileNotFoundError(f"draw.io source file not found: {drawio_path}")

    cmd = [
        str(DRAWIO_EXECUTABLE),
        "--export",
        "--format",
        "png",
        "--scale",
        "2",
        "--crop",
        "--output",
        str(output_path),
        str(drawio_path),
    ]

    subprocess.run(cmd, check=True, timeout=60)
