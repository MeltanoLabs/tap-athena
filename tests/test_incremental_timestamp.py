"""Offline unit tests for temporal replication-key coercion (no AWS required)."""

from __future__ import annotations

import datetime
import typing as t
from unittest import mock

import sqlalchemy as sa

from tap_athena.client import AthenaStream

if t.TYPE_CHECKING:
    from contextlib import AbstractContextManager


def _stream() -> AthenaStream:
    """An AthenaStream instance without running __init__ (no connection needed)."""
    stream = AthenaStream.__new__(AthenaStream)
    stream.replication_key = "eventtimestamp"  # type: ignore[attr-defined]
    return stream


def _patch_super(value: object) -> AbstractContextManager[mock.MagicMock]:
    """Patch the base-class method the override delegates to."""
    return mock.patch(
        "tap_athena.client.SQLStream.get_starting_replication_key_value",
        return_value=value,
    )


def _patch_reflected_type(
    reflected_type: object,
) -> AbstractContextManager[mock.MagicMock]:
    """Stub the reflected replication-key column type."""
    return mock.patch.object(
        AthenaStream,
        "_replication_key_sql_type",
        return_value=reflected_type,
    )


def test_timestamp_column_coerced_to_datetime() -> None:
    """A TIMESTAMP column coerces the string bookmark to a naive-UTC datetime."""
    stream = _stream()
    with (
        _patch_super("2026-06-09T17:39:41.045000+00:00"),
        _patch_reflected_type(sa.types.TIMESTAMP()),
    ):
        result = stream.get_starting_replication_key_value(None)
    assert result == datetime.datetime(2026, 6, 9, 17, 39, 41, 45000)  # noqa: DTZ001
    assert result.tzinfo is None  # naive UTC is the intended output


def test_timestamp_column_with_z_suffix_coerced() -> None:
    """A trailing 'Z' bookmark must coerce on all supported Pythons (incl. 3.10)."""
    stream = _stream()
    with (
        _patch_super("2026-06-09T17:39:41.045000Z"),
        _patch_reflected_type(sa.types.TIMESTAMP()),
    ):
        result = stream.get_starting_replication_key_value(None)
    assert result == datetime.datetime(2026, 6, 9, 17, 39, 41, 45000)  # noqa: DTZ001
    assert result.tzinfo is None  # naive UTC is the intended output


def test_date_column_coerced_to_date() -> None:
    """A DATE column coerces the string bookmark to a date."""
    stream = _stream()
    with (
        _patch_super("2026-06-09T00:00:00+00:00"),
        _patch_reflected_type(sa.types.DATE()),
    ):
        result = stream.get_starting_replication_key_value(None)
    assert result == datetime.date(2026, 6, 9)


def test_varchar_column_left_as_string() -> None:
    """A non-temporal column leaves the bookmark untouched."""
    stream = _stream()
    with (
        _patch_super("2026-06-09T17:39:41.045000+00:00"),
        _patch_reflected_type(sa.types.VARCHAR()),
    ):
        result = stream.get_starting_replication_key_value(None)
    assert result == "2026-06-09T17:39:41.045000+00:00"


def test_non_iso_string_falls_back() -> None:
    """An unparseable bookmark falls back to the raw string."""
    stream = _stream()
    with _patch_super("not-a-timestamp"), _patch_reflected_type(sa.types.TIMESTAMP()):
        result = stream.get_starting_replication_key_value(None)
    assert result == "not-a-timestamp"


def test_no_state_returns_none() -> None:
    """A missing bookmark (no state) returns None unchanged."""
    stream = _stream()
    with _patch_super(None), _patch_reflected_type(sa.types.TIMESTAMP()):
        assert stream.get_starting_replication_key_value(None) is None


def test_unresolved_type_falls_back_to_string() -> None:
    """Reflection failure / unknown column -> _replication_key_sql_type returns None."""
    stream = _stream()
    with _patch_super("2026-06-09T17:39:41.045000+00:00"), _patch_reflected_type(None):
        result = stream.get_starting_replication_key_value(None)
    assert result == "2026-06-09T17:39:41.045000+00:00"


def test_reflection_exception_is_swallowed() -> None:
    """_replication_key_sql_type must never raise, even if reflection blows up."""
    stream = _stream()
    connector = mock.Mock()
    connector.get_table_columns.side_effect = RuntimeError("glue down")
    with (
        mock.patch.object(
            AthenaStream,
            "connector",
            new_callable=mock.PropertyMock,
            return_value=connector,
        ),
        mock.patch.object(
            AthenaStream,
            "fully_qualified_name",
            new_callable=mock.PropertyMock,
            return_value="db.t",
        ),
    ):
        assert stream._replication_key_sql_type() is None  # noqa: SLF001
