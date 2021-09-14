"""Athena tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_athena.client import AthenaStream


class TapAthena(Tap):
    """Athena tap class."""

    name = "tap-athena"
    default_stream_class = AthenaStream

    config_jsonschema = th.PropertiesList(
        th.Property("aws_access_key_id", th.StringType, required=True),
        th.Property("aws_secret_access_key", th.StringType, required=True),
        th.Property("aws_region", th.StringType, required=True),
        th.Property("s3_staging_dir", th.StringType, required=True),
        th.Property("schema_name", th.StringType, required=True),
    ).to_dict()
