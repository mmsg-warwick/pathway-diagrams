# curriculum-diagrams

Generates curriculum dependency diagrams from an Excel workbook. Each sheet in the workbook represents a degree stream (e.g. *Physical Applied Maths*, *Maths Bio*). The pipeline reads module metadata, builds a dependency graph, arranges modules on a grid by year and term, writes a `.drawio` file, and exports a PNG.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management
- [draw.io desktop](https://github.com/jgraph/drawio-desktop/releases) installed at `C:\Program Files\draw.io\draw.io.exe` (used for PNG export)

## Setup

```bash
uv sync --extra dev
```

## Usage

Place your Excel workbook at `input/streams.xlsx`. Each sheet must contain the following columns:

| Column | Description |
|---|---|
| `Module code` | Unique module identifier (e.g. `MA124`) |
| `Module name` | Full module title |
| `CATS` | Credit value |
| `Year` | Academic year (2, 3, or 4) |
| `Term` | Term number (1 or 2) |
| `Status` | One of `ACTIVE`, `NEW`, `REPURPOSED` |
| `Dependencies` | Comma-separated list of prerequisite module codes (can be empty) |

Then run:

```bash
uv run main.py
```

Output files (`.drawio` and `.png`) are written to the `output/` directory, one pair per sheet.

## Running tests

```bash
uv run pytest
```

Coverage is reported to the terminal and written to `coverage.xml`.

## Project structure

```
main.py                  # Entry point
input/                   # Excel workbook goes here
output/                  # Generated diagrams written here
pipeline/
    config.py            # Path to draw.io executable
    load_excel.py        # Load and validate workbook data
    model.py             # Module dataclass, ModuleGraph, dependency validation
    layout.py            # Grid layout engine
    drawio_writer.py     # Build draw.io XML tree
    export.py            # Export .drawio to PNG via draw.io CLI
tests/
    conftest.py          # Shared fixtures
    test_model.py        # Unit tests
```
