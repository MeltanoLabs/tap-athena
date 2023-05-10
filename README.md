# tap-athena

`tap-athena` is a Singer tap for Athena.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

```bash
pipx install git+https://github.com/MeltanoLabs/tap-athena.git
```

## Configuration

### Accepted Config Options

- `aws_access_key_id`
- `aws_secret_access_key`
- `s3_staging_dir`
- `schema_name`
- `aws_region`

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-athena --about
```

### Source Authentication and Authorization

Authentication is performed using AWS credentials, as provided from config settings descried above.

## Usage

You can easily run `tap-athena` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-athena --version
tap-athena --help
tap-athena --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
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

Run tests within the `tests` subfolder:

```bash
poetry run pytest
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
# OR run a test `elt` pipeline:
meltano elt tap-athena target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
