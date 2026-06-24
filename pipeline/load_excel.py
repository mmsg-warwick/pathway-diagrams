"""Load and validate module data from an Excel workbook."""

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "Module code",
    "Module name",
    "CATS",
    "Year",
    "Term",
    "Status",
    "Dependencies",
]


class ValidationError(Exception):
    """Raised when a sheet fails structural or data validation."""


def load_workbook(path: Path) -> dict[str, pd.DataFrame]:
    """Load all sheets from an Excel file and return them as a dict of DataFrames."""
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    return pd.read_excel(path, sheet_name=None)


def validate_columns(df: pd.DataFrame, sheet_name: str) -> None:
    """Raise ValidationError if any required columns are absent from the sheet."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValidationError(f"[{sheet_name}] Missing columns: {missing}")


def clean_string(value: object) -> str:
    """Return the value as a stripped string, or an empty string for NaN."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def parse_dependencies(value: object) -> list[str]:
    """Convert a comma-separated dependency string into a list of module codes."""
    if pd.isna(value) or value == "":
        return []
    return [x.strip() for x in str(value).split(",") if x.strip()]


def validate_and_clean(df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    """Validate structure and contents of a sheet, returning a cleaned copy."""
    validate_columns(df, sheet_name)

    df = df.copy()

    for col in ["Module code", "Module name", "Status", "Dependencies"]:
        df[col] = df[col].apply(clean_string)

    df["Module code"] = df["Module code"].str.upper()

    df["Year"] = pd.to_numeric(df["Year"], errors="raise")
    df["Term"] = pd.to_numeric(df["Term"], errors="raise")

    if not df["Year"].isin([1, 2, 3, 4]).all():
        raise ValidationError(f"[{sheet_name}] Year must be 1, 2, 3, or 4")

    if not df["Term"].isin([1, 2]).all():
        raise ValidationError(f"[{sheet_name}] Term must be 1 or 2")

    if df["Module code"].duplicated().any():
        duplicates = df[df["Module code"].duplicated()]["Module code"].tolist()
        raise ValidationError(f"[{sheet_name}] Duplicate module codes: {duplicates}")

    df["Dependencies"] = df["Dependencies"].apply(parse_dependencies)

    return df


def load_and_validate(path: Path) -> dict[str, pd.DataFrame]:
    """Load an Excel workbook and return a dict of validated, cleaned DataFrames."""
    sheets = load_workbook(path)

    clean_sheets = {}

    for name, df in sheets.items():
        print(f"Validating: {name}")
        clean_sheets[name] = validate_and_clean(df, name)

    return clean_sheets
