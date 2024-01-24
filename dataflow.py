from datetime import timedelta
import os

from bytewax.dataflow import Dataflow
import bytewax.operators as op
from bytewax.testing import TestingSource
from snowflake_connector import SnowflakeSink

from data import cdc_stream

# Database specific info
SOURCE_TABLE_SCHEMA = {"TRIPID": "INT", "DRIVERID": "VARCHAR", "FIELDA": "BOOLEAN"}
PRIMARY_KEY = "TRIPID"  # unique identifier
DESTINATION_TABLE = "DRIVER_TRIPS"

# Snowflake connection parameters
USER = os.getenv("SNOWSQL_USR")
PASSWORD = os.getenv("SNOWSQL_PASS")
WAREHOUSE = os.getenv("SNOWSQL_WAREHOUSE", "COMPUTE_WH")
ACCOUNT = os.getenv("SNOWSQL_ACCOUNT")
DATABASE = "BYTEWAX"
SCHEMA = "PUBLIC"


flow = Dataflow("snowflake-cdc")
change_stream = op.input("input", flow, TestingSource(cdc_stream))
op.inspect("change_stream", change_stream)
batched_stream = op.collect(
    "batch_records", change_stream, timeout=timedelta(seconds=10), max_size=10
)
op.inspect("batched_stream", batched_stream)
op.output(
    "snowflake",
    batched_stream,
    SnowflakeSink(
        USER,
        PASSWORD,
        ACCOUNT,
        WAREHOUSE,
        DATABASE,
        SCHEMA,
        SOURCE_TABLE_SCHEMA,
        PRIMARY_KEY,
        DESTINATION_TABLE,
    ),
)
