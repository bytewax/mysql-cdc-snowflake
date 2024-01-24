# Bytewax Dataflow for Snowflake Database Replication

This repository contains a Bytewax dataflow example that demonstrates how to replicate a database into Snowflake. It's designed to help you understand how to capture and process change data capture (CDC) streams and apply them to a Snowflake database using Bytewax.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.8 or newer installed on your system.
- Access to a Snowflake account with permissions to create tables, insert, update, and delete records.

## Installation

To set up your environment for running the Bytewax dataflow, follow these steps:

1. **Clone the repository:**

```bash
git clone https://github.com/bytewax/your-repository-name.git
cd your-repository-name
```

2. **Install dependencies:**

Using a virtual environment is recommended:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Configuration

Before running the dataflow, you need to configure the Snowflake connection parameters. Set the following environment variables with your Snowflake account details:

```bash
export SNOWSQL_USR=your_username
export SNOWSQL_PASS=your_password
export SNOWSQL_WAREHOUSE=your_warehouse
export SNOWSQL_ACCOUNT=your_account
```

Optionally, you can modify the `DATABASE` and `SCHEMA` variables in `dataflow.py` to match your Snowflake setup.

## Running the Dataflow

To execute the Bytewax dataflow, run the following command:

```bash
python -m bytewax.run dataflow.py
```

This command initiates the dataflow process, which captures changes from the simulated data stream in `data.py`, processes them, and replicates the changes to your Snowflake database.

## Files Description

- `dataflow.py`: The main dataflow script that defines the Bytewax dataflow for capturing and processing CDC events.
- `snowflake_connector.py`: Contains the SnowflakeSink class responsible for connecting to Snowflake and applying the CDC events.
- `data.py`: Simulates a CDC data stream.
- `requirements.txt`: Lists all the Python dependencies required for this project.

## Contributing

We welcome contributions and suggestions! Please create issues or pull requests on our GitHub repository.

## License

Apache 2.0
