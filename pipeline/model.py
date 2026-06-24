"""Domain model: Module data class, ModuleGraph, and graph construction."""

from dataclasses import dataclass

import pandas as pd


@dataclass
class Module:
    """A single teaching module with its metadata and prerequisites."""

    code: str
    name: str
    cats: int
    year: int
    term: int
    status: str
    dependencies: list[str]


class ModelError(Exception):
    """Raised when the module graph contains invalid or inconsistent data."""


class ModuleGraph:
    """Collection of modules indexed by module code."""

    def __init__(self):
        self.modules: dict[str, Module] = {}

    def add_module(self, module: Module) -> None:
        """Add a module, raising ModelError if the code is already present."""
        if module.code in self.modules:
            raise ModelError(f"Duplicate module code: {module.code}")
        self.modules[module.code] = module

    def validate_dependencies(self) -> None:
        """Raise ModelError if any dependency references an unknown module code."""
        for module in self.modules.values():
            for dep in module.dependencies:
                if dep not in self.modules:
                    raise ModelError(f"{module.code} depends on unknown module: {dep}")

    def by_year(self, year: int) -> list[Module]:
        """Return all modules in the given year."""
        return [m for m in self.modules.values() if m.year == year]

    def by_year_term(self, year: int, term: int) -> list[Module]:
        """Return all modules in the given year and term."""
        return [m for m in self.modules.values() if m.year == year and m.term == term]


def build_graph(df: pd.DataFrame) -> ModuleGraph:
    """Construct a ModuleGraph from a validated and cleaned DataFrame."""
    graph = ModuleGraph()

    for _, row in df.iterrows():
        module = Module(
            code=row["Module code"],
            name=row["Module name"],
            cats=int(row["CATS"]) if row["CATS"] != "" else 0,
            year=int(row["Year"]),
            term=int(row["Term"]),
            status=row["Status"],
            dependencies=[d for d in row["Dependencies"].split(",") if d],
        )

        graph.add_module(module)

    graph.validate_dependencies()

    return graph
