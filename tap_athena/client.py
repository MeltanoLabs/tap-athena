"""Custom client handling, including AthenaStream base class."""

from __future__ import annotations

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
        """Generate a SQLAlchemy URL for Athena.

        Args:
            config: Configuration dict for the connector.

        Returns:
            A SQLAlchemy URL for Athena.
        """
        url = (
            f"awsathena+rest://{config['aws_access_key_id']}:"
            f"{config['aws_secret_access_key']}@athena"
            f".{config['aws_region']}.amazonaws.com:443/"
            f"?s3_staging_dir={config['s3_staging_dir']}"
            f"&schema={config['schema_name']}"
            f"&work_group={config['athena_workgroup']}"
        )
        if "aws_session_token" in config:
            url += f"&aws_session_token={config['aws_session_token']}"
        return url


class AthenaStream(SQLStream):
    """The Stream class for Athena."""

    connector_class = AthenaConnector
    supports_nulls_first = True
