"""Athena tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_athena.client import AthenaStream


class TapAthena(Tap):
    """Athena tap class."""

    name = "tap-athena"

    config_jsonschema = th.PropertiesList(
        th.Property("aws_access_key_id", th.StringType, required=True),
        th.Property("aws_secret_access_key", th.StringType, required=True),
        th.Property("aws_region", th.StringType, required=True),
        th.Property("s3_staging_dir", th.StringType, required=True),
        th.Property("schema_name", th.StringType, required=True),
    ).to_dict()

    @property
    def catalog_dict(self) -> dict:
        if self.input_catalog:
            return self.input_catalog.to_dict()

        return AthenaStream.run_discovery(
            self.config,
            schema_filter=[self.config["schema_name"]]
        )

    def discover_streams(self) -> List[AthenaStream]:
        """Return a list of discovered streams."""
        result: List[AthenaStream] = []
        for catalog_entry in self.catalog_dict["streams"]:
            result.append(AthenaStream(self, catalog_entry))

        return result


if __name__ == "__main__":
    TapAthena.cli()
