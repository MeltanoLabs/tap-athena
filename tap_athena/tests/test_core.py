"""Tests standard tap features using the built-in SDK tests library."""

import datetime
from typing import Any, Dict

from singer_sdk.testing import get_standard_tap_tests

from tap_athena.tap import TapAthena

SAMPLE_CONFIG: Dict[str, Any] = {
    # Tap config for tests are loaded from env vars (see `.env.template`)
    # "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
}


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(
        TapAthena,
        config=SAMPLE_CONFIG
    )
    for test in tests:
        test()


# TODO: Create additional tests as appropriate for your tap.
