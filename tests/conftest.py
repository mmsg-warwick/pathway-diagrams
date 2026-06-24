"""Shared test fixtures and utilities."""

import pandas as pd
import pytest


@pytest.fixture
def sample_dataframe():
    """Return a simple valid DataFrame for testing."""
    return pd.DataFrame(
        {
            "Module code": ["CS101", "CS102", "CS201"],
            "Module name": ["Intro to CS", "Data Structures", "Algorithms"],
            "CATS": [10, 10, 20],
            "Year": [2, 2, 3],
            "Term": [1, 2, 1],
            "Status": ["ACTIVE", "ACTIVE", "ACTIVE"],
            "Dependencies": ["", "CS101", "CS101,CS102"],
        }
    )


@pytest.fixture
def sample_dataframe_with_new_status():
    """Return a DataFrame with NEW status modules."""
    return pd.DataFrame(
        {
            "Module code": ["MA101", "MA102"],
            "Module name": ["Calculus", "Linear Algebra"],
            "CATS": [10, 10],
            "Year": [2, 2],
            "Term": [1, 2],
            "Status": ["NEW", "NEW"],
            "Dependencies": ["", ""],
        }
    )


@pytest.fixture
def sample_dataframe_with_repurposed():
    """Return a DataFrame with REPURPOSED status modules."""
    return pd.DataFrame(
        {
            "Module code": ["PH101", "PH102"],
            "Module name": ["Physics I", "Physics II"],
            "CATS": [15, 15],
            "Year": [2, 3],
            "Term": [1, 1],
            "Status": ["REPURPOSED", "ACTIVE"],
            "Dependencies": ["", "PH101"],
        }
    )


@pytest.fixture
def sample_dataframe_complex():
    """Return a more complex DataFrame for layout and edge routing tests."""
    return pd.DataFrame(
        {
            "Module code": ["A", "B", "C", "D", "E", "F"],
            "Module name": [
                "Module A",
                "Module B",
                "Module C",
                "Module D",
                "Module E",
                "Module F",
            ],
            "CATS": [10, 10, 10, 10, 10, 10],
            "Year": [2, 2, 2, 3, 3, 4],
            "Term": [1, 1, 2, 1, 2, 1],
            "Status": ["ACTIVE", "ACTIVE", "ACTIVE", "ACTIVE", "ACTIVE", "ACTIVE"],
            "Dependencies": ["", "A", "A", "B,C", "D", "E"],
        }
    )
