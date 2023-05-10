"""Athena tap class."""

from __future__ import annotations

from singer_sdk import SQLTap
from singer_sdk import typing as th  # JSON schema typing helpers
from tap_athena.client import AthenaStream


class TapAthena(SQLTap):
    """Athena tap class."""

    name = "tap-athena"
    default_stream_class = AthenaStream

    config_jsonschema = th.PropertiesList(
        th.Property(
            "aws_access_key_id",
            th.StringType,
            required=True,
            description="AWS access key ID",
        ),
        th.Property(
            "aws_secret_access_key",
            th.StringType,
            required=True,
            description="AWS secret access key",
        ),
        th.Property(
            "aws_region",
            th.StringType,
            required=True,
            description="AWS region",
        ),
        th.Property(
            "s3_staging_dir",
            th.StringType,
            required=True,
            description=(
                "S3 staging directory. This is where Athena will write output "
                "files."
            ),
        ),
        th.Property(
            "schema_name",
            th.StringType,
            required=True,
            description="Athena schema name",
        ),
    ).to_dict()


if __name__ == "__main__":
    TapAthena.cli()
