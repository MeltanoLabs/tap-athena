"""Custom client handling, including AthenaStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from tap_athena.database import SQLStream
import sqlalchemy


class AthenaStream(SQLStream):
    """Stream class for Athena streams."""

    @classmethod
    def get_sqlalchemy_url(cls, tap_config: dict) -> str:
        return (
            f"awsathena+rest://{tap_config['aws_access_key_id']}:"
            f"{tap_config['aws_secret_access_key']}@athena"
            f".{tap_config['aws_region']}.amazonaws.com:443/?"
            f"s3_staging_dir={tap_config['s3_staging_dir']}"
            f"schema={tap_config['schema_name']}"
        )
