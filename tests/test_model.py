"""Tests for the domain model module."""

import pandas as pd
import pytest

from pipeline.model import ModelError, Module, ModuleGraph, build_graph


class TestModule:
    """Tests for the Module dataclass."""

    def test_module_creation(self):
        """Test basic Module instantiation."""
        module = Module(
            code="CS101",
            name="Intro to CS",
            cats=10,
            year=2,
            term=1,
            status="ACTIVE",
            dependencies=["MA101"],
        )

        assert module.code == "CS101"
        assert module.name == "Intro to CS"
        assert module.cats == 10
        assert module.year == 2
        assert module.term == 1
        assert module.status == "ACTIVE"
        assert module.dependencies == ["MA101"]

    def test_module_with_no_dependencies(self):
        """Test Module with empty dependencies list."""
        module = Module(
            code="CS101",
            name="Intro to CS",
            cats=10,
            year=2,
            term=1,
            status="ACTIVE",
            dependencies=[],
        )

        assert module.dependencies == []


class TestModuleGraph:
    """Tests for the ModuleGraph class."""

    def test_empty_graph(self):
        """Test creating an empty ModuleGraph."""
        graph = ModuleGraph()
        assert len(graph.modules) == 0

    def test_add_single_module(self):
        """Test adding a single module to the graph."""
        graph = ModuleGraph()
        module = Module("CS101", "Intro", 10, 2, 1, "ACTIVE", [])

        graph.add_module(module)

        assert len(graph.modules) == 1
        assert graph.modules["CS101"] == module

    def test_add_multiple_modules(self):
        """Test adding multiple modules to the graph."""
        graph = ModuleGraph()
        modules = [
            Module("CS101", "Intro", 10, 2, 1, "ACTIVE", []),
            Module("CS102", "Data Structures", 10, 2, 2, "ACTIVE", []),
            Module("CS201", "Algorithms", 20, 3, 1, "ACTIVE", []),
        ]

        for module in modules:
            graph.add_module(module)

        assert len(graph.modules) == 3

    def test_duplicate_module_code_raises_error(self):
        """Test that adding duplicate module codes raises ModelError."""
        graph = ModuleGraph()
        module1 = Module("CS101", "Intro", 10, 2, 1, "ACTIVE", [])
        module2 = Module("CS101", "Different Name", 10, 2, 1, "ACTIVE", [])

        graph.add_module(module1)

        with pytest.raises(ModelError, match="Duplicate module code: CS101"):
            graph.add_module(module2)

    def test_validate_dependencies_no_errors(self):
        """Test validate_dependencies with all valid dependencies."""
        graph = ModuleGraph()
        graph.add_module(Module("CS101", "Intro", 10, 2, 1, "ACTIVE", []))
        graph.add_module(
            Module("CS102", "Data Structures", 10, 2, 2, "ACTIVE", ["CS101"])
        )

        graph.validate_dependencies()

    def test_validate_dependencies_missing_dependency(self):
        """Test that validate_dependencies raises error for missing dependencies."""
        graph = ModuleGraph()
        graph.add_module(Module("CS101", "Intro", 10, 2, 1, "ACTIVE", []))
        graph.add_module(
            Module("CS102", "Data Structures", 10, 2, 2, "ACTIVE", ["CS999"])
        )

        with pytest.raises(ModelError, match="CS102 depends on unknown module: CS999"):
            graph.validate_dependencies()

    def test_validate_dependencies_multiple_missing(self):
        """Test validate_dependencies with multiple missing dependencies."""
        graph = ModuleGraph()
        graph.add_module(Module("CS101", "Intro", 10, 2, 1, "ACTIVE", []))
        graph.add_module(
            Module("CS102", "Data Structures", 10, 2, 2, "ACTIVE", ["CS999", "CS888"])
        )

        with pytest.raises(ModelError):
            graph.validate_dependencies()

    def test_by_year(self, sample_dataframe):
        """Test filtering modules by year."""
        graph = build_graph(sample_dataframe)

        year_2_modules = graph.by_year(2)
        year_3_modules = graph.by_year(3)

        assert len(year_2_modules) == 2
        assert len(year_3_modules) == 1

    def test_by_year_term(self, sample_dataframe):
        """Test filtering modules by year and term."""
        graph = build_graph(sample_dataframe)

        y2t1 = graph.by_year_term(2, 1)
        y2t2 = graph.by_year_term(2, 2)
        y3t1 = graph.by_year_term(3, 1)

        assert len(y2t1) == 1
        assert len(y2t2) == 1
        assert len(y3t1) == 1

    def test_by_year_term_empty(self, sample_dataframe):
        """Test filtering for a year/term combination with no modules."""
        graph = build_graph(sample_dataframe)

        y4t2 = graph.by_year_term(4, 2)

        assert len(y4t2) == 0


class TestBuildGraph:
    """Tests for the build_graph function."""

    def test_build_graph_basic(self, sample_dataframe):
        """Test building a graph from a DataFrame."""
        graph = build_graph(sample_dataframe)

        assert len(graph.modules) == 3
        assert "CS101" in graph.modules
        assert "CS102" in graph.modules
        assert "CS201" in graph.modules

    def test_build_graph_preserves_module_data(self, sample_dataframe):
        """Test that build_graph correctly preserves all module data."""
        graph = build_graph(sample_dataframe)

        cs101 = graph.modules["CS101"]
        assert cs101.name == "Intro to CS"
        assert cs101.cats == 10
        assert cs101.year == 2
        assert cs101.term == 1
        assert cs101.status == "ACTIVE"
        assert cs101.dependencies == []

    def test_build_graph_parses_dependencies(self, sample_dataframe):
        """Test that build_graph correctly parses dependency lists."""
        graph = build_graph(sample_dataframe)

        cs102 = graph.modules["CS102"]
        assert cs102.dependencies == ["CS101"]

        cs201 = graph.modules["CS201"]
        assert cs201.dependencies == ["CS101", "CS102"]

    def test_build_graph_validates_on_construction(self):
        """Test that build_graph validates dependencies during construction."""
        df = pd.DataFrame(
            {
                "Module code": ["CS101", "CS102"],
                "Module name": ["Intro", "Advanced"],
                "CATS": [10, 10],
                "Year": [2, 2],
                "Term": [1, 2],
                "Status": ["ACTIVE", "ACTIVE"],
                "Dependencies": ["", "CS999"],
            }
        )

        with pytest.raises(ModelError):
            build_graph(df)

    def test_build_graph_with_new_status(self, sample_dataframe_with_new_status):
        """Test building graph with NEW status modules."""
        graph = build_graph(sample_dataframe_with_new_status)

        assert len(graph.modules) == 2
        assert graph.modules["MA101"].status == "NEW"
        assert graph.modules["MA102"].status == "NEW"

    def test_build_graph_with_repurposed_status(self, sample_dataframe_with_repurposed):
        """Test building graph with REPURPOSED status modules."""
        graph = build_graph(sample_dataframe_with_repurposed)

        assert graph.modules["PH101"].status == "REPURPOSED"
        assert graph.modules["PH102"].status == "ACTIVE"

    def test_build_graph_with_zero_cats(self):
        """Test building graph with modules that have zero CATS."""
        df = pd.DataFrame(
            {
                "Module code": ["CS101"],
                "Module name": ["Intro"],
                "CATS": [""],
                "Year": [2],
                "Term": [1],
                "Status": ["ACTIVE"],
                "Dependencies": [""],
            }
        )

        graph = build_graph(df)
        assert graph.modules["CS101"].cats == 0
