"""Build and serialise draw.io XML trees from a ModuleGraph."""

from xml.etree.ElementTree import Element, ElementTree, SubElement

from pipeline.layout import (
    BOX_HEIGHT,
    BOX_WIDTH,
    TERM_GAP,
    TERM_OFFSET,
    VERTICAL_GAP,
    X_START,
    YEAR_GAP,
    YEAR_LABEL_WIDTH,
    YEAR_SPACING,
)
from pipeline.model import ModuleGraph

# Lane selection order for parallel edges: middle first, then left, then right.
LANE_FRACTIONS = [0.5, 0.25, 0.75]

YEAR_COLOURS = {
    1: "#cfe2ff",  # light blue
    2: "#d9ead3",  # light green
    3: "#fce5cd",  # light orange
    4: "#ead1dc",  # light purple/pink
}


def module_style(module) -> str:
    """Return the draw.io cell style string for a module box."""
    rounded = "1" if module.term == 2 else "0"
    colour = YEAR_COLOURS[module.year]
    return f"rounded={rounded};fillColor={colour};whiteSpace=wrap;"


def get_column_index(module) -> int:
    """Return a linear column index for a module's (year, term) position."""
    return (module.year - 2) * 2 + (module.term - 1)


def adjacent_columns(module1, module2) -> bool:
    """Return True if the two modules sit in neighbouring columns."""
    return abs(get_column_index(module1) - get_column_index(module2)) == 1


def create_base_structure(name: str) -> tuple[Element, Element]:
    """Create the root mxfile element and return (mxfile, root) for further population."""
    mxfile = Element("mxfile", host="Electron")
    diagram = SubElement(mxfile, "diagram", name=name)

    model = SubElement(
        diagram,
        "mxGraphModel",
        dx="2404",
        dy="1203",
        grid="1",
        gridSize="10",
        guides="1",
    )

    root = SubElement(model, "root")

    SubElement(root, "mxCell", id="0")
    SubElement(root, "mxCell", id="1", parent="0")

    return mxfile, root


def module_label(module) -> str:
    """Return the display text for a module cell, prefixed by status if notable."""
    status = module.status.upper()

    if status == "NEW":
        prefix = "[NEW]"
    elif status == "REPURPOSED":
        prefix = "[REPURPOSED]"
    else:
        prefix = module.code

    return f"{prefix} {module.name}"


def add_module_cell(root, module, x: int, y: int) -> None:
    """Append an mxCell vertex for a module to the XML root."""
    cell = SubElement(
        root,
        "mxCell",
        {
            "id": module.code,
            "value": module_label(module),
            "style": module_style(module),
            "vertex": "1",
            "parent": "1",
        },
    )

    SubElement(
        cell,
        "mxGeometry",
        {
            "x": str(x),
            "y": str(y),
            "width": str(BOX_WIDTH),
            "height": str(BOX_HEIGHT),
            "as": "geometry",
        },
    )


def add_year_labels(root) -> None:
    """Append year heading labels centred over each year's two columns."""
    for i, year in enumerate([2, 3, 4]):
        base_x = X_START + i * YEAR_SPACING
        center_x = base_x + TERM_OFFSET / 2 + BOX_WIDTH / 2

        cell = SubElement(
            root,
            "mxCell",
            {
                "id": f"label_y{year}",
                "value": f"Year {year}",
                "style": "text;fontStyle=1;align=center;fontSize=20;",
                "vertex": "1",
                "parent": "1",
            },
        )

        SubElement(
            cell,
            "mxGeometry",
            {
                "x": str(center_x - YEAR_LABEL_WIDTH / 2),
                "y": "45",
                "width": str(YEAR_LABEL_WIDTH),
                "height": "30",
                "as": "geometry",
            },
        )


def add_term_labels(root) -> None:
    """Append T1/T2 labels beneath each year heading."""
    for i, year in enumerate([2, 3, 4]):
        base_x = X_START + i * YEAR_SPACING

        for term, label in [(1, "T1"), (2, "T2")]:
            x = base_x + (term - 1) * TERM_OFFSET + BOX_WIDTH / 2

            cell = SubElement(
                root,
                "mxCell",
                {
                    "id": f"t{term}_y{year}",
                    "value": label,
                    "style": "text;align=center;verticalAlign=middle;fontSize=14;",
                    "vertex": "1",
                    "parent": "1",
                },
            )

            SubElement(
                cell,
                "mxGeometry",
                {
                    "x": str(x - 20),
                    "y": "85",
                    "width": "40",
                    "height": "20",
                    "as": "geometry",
                },
            )


def get_vertical_lanes_for_box(x: int, module, role: str) -> list[float]:
    """Return three x-coordinates in the gap beside a module box.

    role is "source" (gap to the right) or "target" (gap to the left).
    """
    if role == "source":
        gap_width = TERM_GAP if module.term == 1 else YEAR_GAP
        base = x + BOX_WIDTH
    elif role == "target":
        gap_width = YEAR_GAP if module.term == 1 else TERM_GAP
        base = x - gap_width
    else:
        raise ValueError(f"Invalid role: {role}")

    return [base + frac * gap_width for frac in LANE_FRACTIONS]


def get_horizontal_lanes(y1: int, y2: int) -> list[float]:
    """Return three y-coordinates for horizontal routing segments.

    Lanes are placed below the source box when source is above target (or same
    row), and above the source box otherwise.
    """
    if abs(y1 - y2) < 5 or y1 < y2:
        base = y1 - VERTICAL_GAP
    else:
        base = y1 + BOX_HEIGHT

    return [base + frac * VERTICAL_GAP for frac in LANE_FRACTIONS]


def compute_edge_route(
    source_id: str,
    target_id: str,
    positions: dict,
    graph: ModuleGraph,
    edge_idx: int,
) -> list[tuple[float, float]]:
    """Compute orthogonal waypoints for an edge between two modules.

    Adjacent-column edges with matching rows are drawn directly; all others
    receive two or four waypoints to avoid overlapping boxes.
    """
    x1, y1 = positions[source_id]
    x2, y2 = positions[target_id]

    y1c = y1 + BOX_HEIGHT / 2
    y2c = y2 + BOX_HEIGHT / 2

    adjacent = adjacent_columns(graph.modules[source_id], graph.modules[target_id])
    same_row = abs(y1 - y2) < 1

    if adjacent:
        if same_row:
            return []

        # One vertical detour through the gap between columns.
        source_module = graph.modules[source_id]
        vertical_lanes = get_vertical_lanes_for_box(x1, source_module, "source")
        lane_x = vertical_lanes[edge_idx % 3]
        return [(lane_x, y1c), (lane_x, y2c)]

    # Non-adjacent: route via vertical gaps on both sides plus a horizontal lane.
    source_module = graph.modules[source_id]
    target_module = graph.modules[target_id]

    lanes_src = get_vertical_lanes_for_box(x1, source_module, "source")
    lanes_tgt = get_vertical_lanes_for_box(x2, target_module, "target")

    lane_src_x = lanes_src[edge_idx % 3]
    lane_tgt_x = lanes_tgt[edge_idx % 3]

    lane_y = get_horizontal_lanes(y1, y2)[edge_idx % 3]

    return [
        (lane_src_x, y1c),  # out from source
        (lane_src_x, lane_y),  # vertical to horizontal level
        (lane_tgt_x, lane_y),  # horizontal across
        (lane_tgt_x, y2c),  # down/up to target
    ]


def add_edge(
    root,
    graph: ModuleGraph,
    source_id: str,
    target_id: str,
    positions: dict,
    edge_id: str,
    edge_idx: int,
) -> None:
    """Append an orthogonal mxCell edge with computed waypoints to the XML root."""
    cell = SubElement(
        root,
        "mxCell",
        {
            "id": edge_id,
            "edge": "1",
            "parent": "1",
            "source": source_id,
            "target": target_id,
            "style": (
                "edgeStyle=orthogonalEdgeStyle;"
                "rounded=1;"
                "orthogonalLoop=1;"
                "jettySize=auto;"
                "html=1;"
                "endArrow=block;"
                "strokeWidth=2;"
                "jumpStyle=arc;"
                "jumpSize=6;"
                "exitX=1;exitY=0.5;"
                "entryX=0;entryY=0.5;"
            ),
        },
    )

    geometry = SubElement(
        cell,
        "mxGeometry",
        {"relative": "1", "as": "geometry"},
    )

    route_points = compute_edge_route(source_id, target_id, positions, graph, edge_idx)

    points_el = SubElement(geometry, "Array", {"as": "points"})
    for x, y in route_points:
        SubElement(points_el, "mxPoint", {"x": str(x), "y": str(y)})


def add_edges(root, graph: ModuleGraph, positions: dict) -> None:
    """Append an edge cell for every module dependency in the graph."""
    edge_counter = 0

    for module in graph.modules.values():
        for dep in module.dependencies:
            if dep not in graph.modules:
                continue

            add_edge(
                root,
                graph,
                dep,
                module.code,
                positions,
                f"edge_{edge_counter}",
                edge_counter,
            )

            edge_counter += 1


def build_drawio_tree(name: str, graph: ModuleGraph, positions: dict) -> ElementTree:
    """Build and return a complete draw.io ElementTree for the given graph."""
    mxfile, root = create_base_structure(name)

    for module in graph.modules.values():
        x, y = positions[module.code]
        add_module_cell(root, module, x, y)

    add_edges(root, graph, positions)

    add_year_labels(root)
    add_term_labels(root)

    return ElementTree(mxfile)


def save_drawio(tree: ElementTree, output_path) -> None:
    """Write a draw.io ElementTree to disk as UTF-8 XML."""
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
