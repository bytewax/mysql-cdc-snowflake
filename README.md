# Bytewax Dataflow for Snowflake Database Replication

This repository contains a Bytewax dataflow example that demonstrates how to replicate a MySQL database into Snowflake. It's designed to help you understand how to capture and process change data capture (CDC) streams and apply them to a Snowflake database using Bytewax.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.10 or newer installed on your system.
- Access to a Snowflake account with permissions to create tables, insert, update, and delete records.
- Docker installed

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

before getting started, we need to run mysql.

`docker compose up -d`

The key lines in docker compose are:

```docker
    environment:
      MYSQL_ROOT_PASSWORD: example
      MYSQL_DATABASE: bytewax
    command: --server-id=1 --log-bin=mysql-bin --binlog-format=ROW --binlog_row_image=FULL --binlog_row_metadata=FULL
    volumes: 
          - ./init:/docker-entrypoint-initdb.d
    ports:
      - "3306:3306"
```

We set the root password and the default database.

Then we configure the database with the binlog format and the row metadata and image to get all of the metadata we need for replication in the binlog.

When docker starts up it will look for an init file and we have mounted the volume init volume to our docker-entrypoint-initdb folder. This will be used to set the database up with some commands. Mainly to turn on the replication, and create a bytewax database with our trips table in it.

```sql
CREATE USER 'replicator'@'%' IDENTIFIED BY 'replicationpassword';
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
FLUSH PRIVILEGES;
create database bytewax;
use bytewax;
CREATE TABLE trips (
    TRIPID INT PRIMARY KEY,
    DRIVERID INT,
    TIMECOMPLETED TIMESTAMP,
);
```

Now we have MySQL configured. The next step is to simulate some activity.

### Simulating Data

The `data/simulation.py` file will create, modify and delete trips to create a replication log.

We could now run the dataflow and the simulation python files without the snowflake connector to show the output of the binlog.

## Configuring Snowflake

Before running the dataflow, you need to configure the Snowflake connection parameters. Set the following environment variables with your Snowflake account details:

```bash
export SNOWSQL_USR=your_username
export SNOWSQL_PASS=your_password
export SNOWSQL_WAREHOUSE=your_warehouse
export SNOWSQL_ACCOUNT=your_account
```

You can get the account identifier from the url as the first part of the url.
`https://********-*******.us-east-1.snowflakecomputing.com`

Optionally, you can modify the `DATABASE` and `SCHEMA` variables in `dataflow.py` to match your Snowflake setup.

## Running the Dataflow

To execute the Bytewax dataflow, run the following command:

```bash
python -m bytewax.run dataflow.py
```

This command initiates the dataflow process, which captures changes from the binlog, processes them, and replicates the changes to your Snowflake database.

Once the dataflow is running you can run the simulation file with:

```bash
python data/simulation.py
```

You should then be able to see your changes in Snowflake.

## Files Description

- `dataflow.py`: The main dataflow script that defines the Bytewax dataflow for capturing and processing CDC events.
- `mysql_connector.py`: Contains the connector code to read the MySQL changes in the binlog.
- `snowflake_connector.py`: Contains the SnowflakeSink class responsible for connecting to Snowflake and applying the CDC events.
- `simulation.py`: A simulation of trips being logged, modified and deleted.
- `requirements.txt`: Lists all the Python dependencies required for this project.

## Contributing

We welcome contributions and suggestions! Please create issues or pull requests on our GitHub repository.

## License

Apache 2.0
