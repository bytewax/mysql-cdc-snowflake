from datetime import timedelta
import os

from bytewax.dataflow import Dataflow
import bytewax.operators as op
from bytewax.operators.helpers import map_dict_value
from connectors.mysql_connector import MySQLBinLogSource
from connectors.snowflake_connector import SnowflakeSink

mysql_settings = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "passwd": "example"
}

# Database specific info
SOURCE_TABLE_SCHEMA = {"TRIPID": "INT", "DRIVERID": "VARCHAR", "TIMECOMPLETED": "TIMESTAMP"}
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
change_stream = op.input("input", flow, MySQLBinLogSource(mysql_settings))
op.inspect("change_stream", change_stream)
change_stream = op.flatten("1-many", change_stream)
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
