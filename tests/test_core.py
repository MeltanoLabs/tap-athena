"""Tests standard tap features using the built-in SDK tests library."""
from __future__ import annotations

import json
from pathlib import Path

from singer_sdk.testing import get_tap_test_class

from tap_athena.tap import TapAthena

SAMPLE_CONFIG = json.loads(Path(".secrets/config.json").read_text())

TestTapAthena = get_tap_test_class(
    tap_class=TapAthena,
    config=SAMPLE_CONFIG,
    catalog="tests/catalog.json",
)
