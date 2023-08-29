"""Custom client handling, including AthenaStream base class."""

from __future__ import annotations

import typing as t

import sqlalchemy
from singer_sdk import SQLConnector, SQLStream

if t.TYPE_CHECKING:
    from sqlalchemy.engine import Engine


class AthenaConnector(SQLConnector):
    """The connector for SQLite.

    This class handles all DDL and type conversions.
    """

    allow_temp_tables = False
    allow_column_alter = False
    allow_merge_upsert = True

    def get_sqlalchemy_url(self, config: dict[str, t.Any]) -> str:
        """Generates a SQLAlchemy URL for Athena.

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

    def create_engine(self) -> Engine:
        """Create a SQLAlchemy engine.

        Returns:
            A SQLAlchemy engine.
        """
        return sqlalchemy.create_engine(
            self.sqlalchemy_url,
            echo=False,
            # TODO: Enable JSON serialization/deserialization.
            # https://github.com/MeltanoLabs/tap-athena/issues/35
            # json_serializer=self.serialize_json,
            # json_deserializer=self.deserialize_json,
        )


class AthenaStream(SQLStream):
    """The Stream class for Athena."""

    connector_class = AthenaConnector
