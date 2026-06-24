"""Entry point for curriculum diagram generation.

Loads module data from an Excel workbook, builds a dependency graph for each
sheet, computes a grid layout, writes a draw.io file, and exports a PNG.
"""

from pathlib import Path

from pipeline.drawio_writer import build_drawio_tree, save_drawio
from pipeline.export import export_to_png
from pipeline.layout import layout_graph
from pipeline.load_excel import load_and_validate
from pipeline.model import build_graph

INPUT_PATH = Path("input/streams.xlsx")
OUTPUT_DIR = Path("output")


def main():
    """Run the full diagram generation pipeline for every sheet in the workbook."""
    sheets = load_and_validate(INPUT_PATH)

    OUTPUT_DIR.mkdir(exist_ok=True)

    for name, df in sheets.items():
        print(f"Generating diagram: {name}")

        graph = build_graph(df)
        positions = layout_graph(graph)

        tree = build_drawio_tree(name, graph, positions)

        output_file = OUTPUT_DIR / f"{name}.drawio"
        save_drawio(tree, output_file)

        print(f"Saved: {output_file}")

        png_file = output_file.with_suffix(".png")
        export_to_png(output_file, png_file)

    print("\nDiagrams generated successfully")


if __name__ == "__main__":
    main()
