"""Custom client handling, including AthenaStream base class."""

from __future__ import annotations

import datetime
import typing as t

import sqlalchemy as sa
from singer_sdk import SQLConnector, SQLStream

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


class AthenaConnector(SQLConnector):
    """The connector for SQLite.

    This class handles all DDL and type conversions.
    """

    allow_temp_tables = False
    allow_column_alter = False
    allow_merge_upsert = True

    def get_sqlalchemy_url(self, config: dict[str, t.Any]) -> str:
        """Generate a SQLAlchemy URL for Athena.

        Args:
            config: Configuration dict for the connector.

        Returns:
            A SQLAlchemy URL for Athena.
        """
        return (
            f"awsathena+rest://{config['aws_access_key_id']}:"
            f"{config['aws_secret_access_key']}@athena"
            f".{config['aws_region']}.amazonaws.com:443/?"
            f"s3_staging_dir={config['s3_staging_dir']}"
            f"schema={config['schema_name']}"
        )


class AthenaStream(SQLStream):
    """The Stream class for Athena."""

    connector_class = AthenaConnector
    supports_nulls_first = True

    def get_starting_replication_key_value(
        self,
        context: Context | None,
    ) -> t.Any | None:  # noqa: ANN401
        """Override for SQLStream.get_starting_replication_key_value.

        Returns the incremental bookmark as per usual, then coerces the data
        type to a datetime for temporal keys.

        Without the override, any column in Athena with a TIMESTAMP/DATE type
        would fail because of a TYPE_MISMATCH (timestamp <= varchar). This is
        because Pyathena formats the current checkpoint as a varchar literal,
        while the underlying Athena column is a TIMESTAMP or DATE.

        This only affects streams whose replication key is marked as a
        Timestamp or Date data type, and does not affect streams whose
        replication keys are of other data types.

        Args:
            context: Stream partition or context dictionary.

        Returns:
            The starting replication value. For keys that are temporal, the
            bookmark/checkpoint is returned in a datetime or date data type.
            Otherwise the bookmark/checkpoint is left as is.
        """
        # Accesses its parent class method and executes it before continuing.
        start_val = super().get_starting_replication_key_value(context)

        # If the replication key is not set or the start value is not a
        # string, return it as-is.
        if not self.replication_key or not isinstance(start_val, str):
            return start_val

        column_type = self._replication_key_sql_type()
        if column_type is None:
            return start_val

        # sa.types.TIMESTAMP subclasses DateTime; sa.types.DATE subclasses Date.
        if isinstance(column_type, sa.types.DateTime):
            parsed = self._to_naive_utc_datetime(start_val)
            return parsed if parsed is not None else start_val
        if isinstance(column_type, sa.types.Date):
            parsed = self._to_naive_utc_datetime(start_val)
            return parsed.date() if parsed is not None else start_val
        return start_val

    def _replication_key_sql_type(self) -> sa.types.TypeEngine | None:
        """Reflect the replication key's true Athena column type.

        Returns ``None`` if the type cannot be determined; reflection failures
        must never break a sync, so callers fall back to the raw string
        bookmark.
        """
        try:
            columns = self.connector.get_table_columns(
                full_table_name=self.fully_qualified_name,
                column_names=[self.replication_key],
            )
        except Exception:  # noqa: BLE001 — reflection must never break a sync
            return None

        target = self.replication_key.casefold()
        for name, column in columns.items():
            if name.casefold() == target:
                return column.type
        return None

    @staticmethod
    def _to_naive_utc_datetime(value: str) -> datetime.datetime | None:
        # Python 3.10's datetime.fromisoformat() cannot parse a trailing "Z";
        # normalise it to "+00:00" so UTC bookmarks coerce correctly there too.
        normalised = value[:-1] + "+00:00" if value.endswith(("Z", "z")) else value
        try:
            parsed = datetime.datetime.fromisoformat(normalised)
        except ValueError:
            return None

        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(datetime.timezone.utc).replace(tzinfo=None)

        return parsed
