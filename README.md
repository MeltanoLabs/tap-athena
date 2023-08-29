# `tap-athena`

Athena tap class.

Built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`

## Settings

| Setting              | Required | Default | Description |
|:---------------------|:--------:|:-------:|:------------|
| aws_access_key_id    | True     | None    |             |
| aws_secret_access_key| True     | None    |             |
| aws_region           | True     | None    |             |
| s3_staging_dir       | True     | None    |             |
| schema_name          | True     | None    |             |
| stream_maps          | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config    | False    | None    | User-defined config values to be used within map expressions. |
| flattening_enabled   | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth | False    | None    | The max depth to flatten schemas. |

A full list of supported settings and capabilities is available by running: `tap-athena --about`

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

## Usage

You can easily run `tap-athena` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-athena --version
tap-athena --help
tap-athena --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
# Install pipx if you haven't already
pip install pipx
pipx ensurepath

# Restart your terminal here, if needed, to get the updated PATH
pipx install poetry

# Optional: Install Tox if you want to use it to run auto-formatters, linters, tests, etc.
pipx install tox
```

### Create and Run Tests

To run the automated tests, create the following test table in Athena. Make sure to alter to use your database name and S3 path.

```sql
CREATE EXTERNAL TABLE `my_sample_data`.`test_data` (
  `complex-1` decimal(1),
  `complex_2` int,
  `Complex3` array < string >,
  `complex_4_date` date,
  `complex_5_bool` boolean,
  `complex_6_float` float,
  `complex_7_timestamp` timestamp
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES ('field.delim' = ',')
STORED AS INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat' OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 's3://[YOUR_BUKET_NAME]/complex_data/'
TBLPROPERTIES (
  'classification' = 'csv',
  'skip.header.line.count' = '0',
  'write.compression' = 'GZIP'
);


INSERT INTO "test_data" values(cast(2.0 as decimal(1,0)),2,ARRAY['d','e','f'], cast('2023-05-11' as date),false,cast(2.001 as real), CAST('2023-05-02 02:02:02.02' as  TIMESTAMP));

select * from "test_data";
```

Add your config.json to the `.secrets` directory:

Create tests within the `tests` subfolder and
  then run:

```bash
pipx run tox -e pytest
pipx run tox -e pytest -- tests/test_core.py
```

You can also test the `tap-athena` CLI interface directly using `poetry run`:

```bash
poetry run tap-athena --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-athena
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-athena --version
# OR run a test `run` pipeline:
meltano run tap-athena target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
