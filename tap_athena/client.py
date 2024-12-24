"""Custom client handling, including AthenaStream base class."""

from __future__ import annotations

import os
import typing as t

from singer_sdk import SQLConnector, SQLStream
from sqlalchemy.engine.url import URL


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
        # Get the required parameters from config file and/or environment variables
        aws_access_key_id = config.get("aws_access_key_id") or os.environ.get(
            "AWS_ACCESS_KEY_ID"
        )
        aws_secret_access_key = config.get("aws_secret_access_key") or os.environ.get(
            "AWS_SECRET_ACCESS_KEY"
        )
        aws_session_token = config.get("aws_session_token") or os.environ.get(
            "AWS_SESSION_TOKEN"
        )
        aws_region = config.get("aws_region") or os.environ.get("AWS_REGION")
        s3_staging_dir = config.get("s3_staging_dir") or os.environ.get("S3_STAGING_DIR")
        athena_workgroup = config.get("athena_workgroup") or os.environ.get(
            "ATHENA_WORKGROUP"
        )

        query = {
            "s3_staging_dir": s3_staging_dir,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "region_name": aws_region,
            "work_group": athena_workgroup,
        }
        if aws_session_token:
            query["aws_session_token"] = aws_session_token
        url = URL.create(
            drivername="awsathena+rest",
            host=f"athena.{aws_region}.amazonaws.com",
            database=config['schema_name'],
            query=query
        )
        return str(url)


class AthenaStream(SQLStream):
    """The Stream class for Athena."""

    connector_class = AthenaConnector
    supports_nulls_first = True
