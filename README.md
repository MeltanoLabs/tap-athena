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

Create tests within the `tap_athena/tests` subfolder and
  then run:

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
