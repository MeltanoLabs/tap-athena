"""Custom client handling, including AthenaStream base class."""

import typing as t

from singer_sdk import SQLConnector, SQLStream


class AthenaConnector(SQLConnector):
    """The connector for SQLite.

    This class handles all DDL and type conversions.
    """

    allow_temp_tables = False
    allow_column_alter = False
    allow_merge_upsert = True

    def get_sqlalchemy_url(self, config: dict[str, t.Any]) -> str:
        """Generates a SQLAlchemy URL for Athena."""
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
