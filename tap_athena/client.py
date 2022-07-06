"""Custom client handling, including AthenaStream base class."""

from singer_sdk import SQLConnector, SQLStream


class AthenaConnector(SQLConnector):
    """Connects to the Athena SQL source."""

    def get_sqlalchemy_url(cls, config: dict) -> str:
        return (
            f"awsathena+rest://{config['aws_access_key_id']}:"
            f"{config['aws_secret_access_key']}@athena"
            f".{config['aws_region']}.amazonaws.com:443/"
            f"{config['schema_name']}?"
            f"s3_staging_dir={config['s3_staging_dir']}"
        )


class AthenaStream(SQLStream):
    """Stream class for Athena streams."""

    connector_class = AthenaConnector
