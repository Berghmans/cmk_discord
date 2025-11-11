#!/usr/bin/env python3
"""
Utility module for loading test data from JSON files.
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path to import cmk_discord
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'notifications')))

import cmk_discord


def get_data_dir(version: str = "2.2.0p21") -> Path:
    """Get the data directory for a specific CheckMK version."""
    tests_dir = Path(__file__).parent
    return tests_dir / "data" / version


def load_test_data(filename: str, version: str = "2.2.0p21") -> cmk_discord.Context:
    """
    Load test data from a JSON file and return as Context object.

    Args:
        filename: Name of the JSON file (can include subdirectory like 'service/problem_critical.json')
        version: CheckMK version (default: 2.2.0p21)

    Returns:
        Context object containing the test data
    """
    data_dir = get_data_dir(version)
    file_path = data_dir / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, 'r') as f:
        data = json.load(f)

    # Strip NOTIFY_ prefix (simulates what Context.from_env() does)
    stripped_data = {
        key[7:] if key.startswith("NOTIFY_") else key: value
        for key, value in data.items()
    }

    return cmk_discord.Context.from_dict(stripped_data)


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
    return sorted(versions, reverse=True)  # Latest version first


def get_latest_version() -> str:
    """Get the latest (most recent) CheckMK version available."""
    versions = get_available_versions()
    if not versions:
        raise ValueError("No test data versions found")
    return versions[0]  # First item is latest due to reverse sort


def load_latest_test_data(category: str, filename: str) -> cmk_discord.Context:
    """
    Load test data from the latest version that has the specified file.

    Args:
        category: 'service' or 'host'
        filename: Name of the file (e.g., 'problem_critical.json')

    Returns:
        Context object containing the test data from the latest available version
    """
    versions = get_available_versions()

    for version in versions:
        filepath = f"{category}/{filename}"
        data_dir = get_data_dir(version)
        full_path = data_dir / filepath

        if full_path.exists():
            return load_test_data(filepath, version=version)

    raise FileNotFoundError(f"Test data file {category}/{filename} not found in any version")


def get_all_test_cases(version: str = "2.2.0p21") -> Dict[str, List[str]]:
    """
    Get all test cases organized by type.

    Returns:
        Dictionary with 'service' and 'host' keys containing lists of test file paths
    """
    test_cases = {"service": [], "host": []}

    service_files = list_test_data_files("service", version)
    host_files = list_test_data_files("host", version)

    test_cases["service"] = service_files
    test_cases["host"] = host_files

    return test_cases


def generate_test_params_for_all_versions():
    """
    Generate test parameters for all versions and all test files.

    Returns:
        List of tuples (version, category, filepath, filename) for parameterization
    """
    params = []
    versions = get_available_versions()

    for version in versions:
        test_cases = get_all_test_cases(version)
        for category, files in test_cases.items():
            for filepath in files:
                filename = Path(filepath).stem  # Get filename without extension
                params.append((version, category, filepath, filename))

    return params
