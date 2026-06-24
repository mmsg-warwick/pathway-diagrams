"""Grid layout engine: assigns (x, y) canvas positions to each module."""

from pipeline.model import Module, ModuleGraph

# Layout constants
X_START = -300
YEAR_SPACING = 520
TERM_OFFSET = 240

Y_START = 120
ROW_HEIGHT = 110
BOX_WIDTH = 180
BOX_HEIGHT = 60

YEAR_LABEL_WIDTH = 200

TERM_GAP = TERM_OFFSET - BOX_WIDTH
YEAR_GAP = YEAR_SPACING - TERM_GAP - 2 * BOX_WIDTH
VERTICAL_GAP = ROW_HEIGHT - BOX_HEIGHT


def compute_x(year: int, term: int) -> int:
    """Return the left edge x-coordinate for the given year/term column."""
    x = X_START + (year - 2) * YEAR_SPACING
    if term == 2:
        x += TERM_OFFSET
    return x


def sort_modules(modules: list[Module]) -> list[Module]:
    """Return modules sorted by code for a deterministic column ordering."""
    return sorted(modules, key=lambda m: m.code)


def layout_graph(graph: ModuleGraph) -> dict[str, tuple[int, int]]:
    """Assign pixel positions to each module on the canvas.

    Returns:
        Mapping of module_code to (x, y) top-left corner coordinates.
    """
    positions = {}

    for year in [2, 3, 4]:
        for term in [1, 2]:
            modules = graph.by_year_term(year, term)

            for i, module in enumerate(modules):
                x = compute_x(year, term)
                y = Y_START + i * ROW_HEIGHT

                positions[module.code] = (x, y)

    return positions
