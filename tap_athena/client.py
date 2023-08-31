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
            # json_serializer=self.serialize_json,  # noqa: ERA001
            # json_deserializer=self.deserialize_json,  # noqa: ERA001
        )


class AthenaStream(SQLStream):
    """The Stream class for Athena."""

    connector_class = AthenaConnector

    # Get records from stream
    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """Return a generator of record-type dictionary objects.

        If the stream has a replication_key value defined, records will be sorted by the
        incremental key. If the stream also has an available starting bookmark, the
        records will be filtered for values greater than or equal to the bookmark value.

        Args:
            context: If partition context is provided, will read specifically from this
                data slice.

        Yields:
            One dict per record.

        Raises:
            NotImplementedError: If partition is passed in context and the stream does
                not support partitioning.
        """
        if context:
            raise NotImplementedError(
                f"Stream '{self.name}' does not support partitioning.",
            )

        selected_column_names = self.get_selected_schema()["properties"].keys()
        table = self.connector.get_table(
            full_table_name=self.fully_qualified_name,
            column_names=selected_column_names,
        )
        query = table.select()

        if self.config["paginate"] or self.replication_key:
            if self.config["paginate"] and not self.replication_key:
                raise Exception("Replication key is required when paginate is set.")
            replication_key_col = table.columns[self.replication_key]
            query = query.order_by(replication_key_col)

            start_val = self.get_starting_replication_key_value(context)
            if start_val:
                query = query.where(
                    sqlalchemy.text(":replication_key >= :start_val").bindparams(
                        replication_key=replication_key_col,
                        start_val=start_val,
                    ),
                )

        if self.ABORT_AT_RECORD_COUNT is not None:
            # Limit record count to one greater than the abort threshold. This ensures
            # `MaxRecordsLimitException` exception is properly raised by caller
            # `Stream._sync_records()` if more records are available than can be
            # processed.
            query = query.limit(self.ABORT_AT_RECORD_COUNT + 1)


        if self.config["paginate"]:
            batch_start = 0
            batch_size = self.config["paginate_batch_size"]
            batch_end = batch_size
            with self.connector._connect() as conn:
                record_count = 0
                while True:
                    full_query  = query.limit(batch_end).offset(batch_start)
                    for record in conn.execute(full_query):
                        yield dict(record._mapping)
                        record_count += 1
                    if record_count < batch_size:
                        break
                    else:
                        batch_end = batch_end + batch_size
                        batch_start = batch_start + batch_size
                        record_count = 0
        else:
            with self.connector._connect() as conn:
                for record in conn.execute(query):
                    yield dict(record._mapping)
