"""Tests standard tap features using the built-in SDK tests library."""

import json

from singer_sdk.testing import get_tap_test_class
from tap_athena.tap import TapAthena

SAMPLE_CONFIG = json.load(open(".secrets/config.json"))

TestTapAthena = get_tap_test_class(
    tap_class=TapAthena,
    config=SAMPLE_CONFIG,
    catalog="tests/catalog.json",
)
