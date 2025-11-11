#!/usr/bin/env python3
"""
Utility module for loading test data from JSON files.
"""
import json
import os
from pathlib import Path
from typing import Dict, List


def get_data_dir(version: str = "2.2.0p21") -> Path:
    """Get the data directory for a specific CheckMK version."""
    tests_dir = Path(__file__).parent
    return tests_dir / "data" / version


def load_test_data(filename: str, version: str = "2.2.0p21", strip_notify_prefix: bool = True) -> Dict:
    """
    Load test data from a JSON file.

    Args:
        filename: Name of the JSON file (can include subdirectory like 'service/problem_critical.json')
        version: CheckMK version (default: 2.2.0p21)
        strip_notify_prefix: If True, strip 'NOTIFY_' prefix from keys (simulates build_context())

    Returns:
        Dictionary containing the test data context
    """
    data_dir = get_data_dir(version)
    file_path = data_dir / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, 'r') as f:
        data = json.load(f)

    if strip_notify_prefix:
        # Simulate what build_context() does: strip NOTIFY_ prefix
        return {
            key[7:] if key.startswith("NOTIFY_") else key: value
            for key, value in data.items()
        }

    return data


def list_test_data_files(category: str = None, version: str = "2.2.0p21") -> List[str]:
    """
    List all available test data files.

    Args:
        category: Optional category filter ('service' or 'host')
        version: CheckMK version (default: 2.2.0p21)

    Returns:
        List of available test data file paths (relative to version directory)
    """
    data_dir = get_data_dir(version)

    if category:
        search_dir = data_dir / category
        if not search_dir.exists():
            return []
        files = list(search_dir.glob("*.json"))
        return [f"{category}/{f.name}" for f in files]
    else:
        # Get all JSON files recursively
        files = list(data_dir.glob("**/*.json"))
        return [str(f.relative_to(data_dir)) for f in files]


def get_available_versions() -> List[str]:
    """Get list of available CheckMK versions in test data."""
    tests_dir = Path(__file__).parent
    data_dir = tests_dir / "data"

    if not data_dir.exists():
        return []

    versions = [d.name for d in data_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    return sorted(versions)
