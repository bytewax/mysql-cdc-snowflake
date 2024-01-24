from bytewax.outputs import StatelessSinkPartition, DynamicSink
import snowflake.connector


def create_temp_table(table_data, destination_table, stream_table_schema):
    """Create a temporary stream table statement.

    Arguments:
    table_data - dictionary of change data used to generate the table.
    """
    columns__types = ", ".join(
        [" ".join(key__value) for key__value in stream_table_schema.items()]
    )
    query_string = f"""CREATE OR REPLACE TABLE temp_{destination_table}_stream ({columns__types});"""

    columns = ", ".join(stream_table_schema.keys())
    values = ", ".join(
        [
            "(" + ", ".join([str(row[x]) for x in stream_table_schema.keys()]) + ")"
            for row in table_data
        ]
    )
    insert_string = f"""INSERT INTO temp_{destination_table}_stream ({columns})
                    VALUES {values};""".replace(
        "None", "NULL"
    )
    return (query_string, insert_string)


def merge_table(destination_table, destination_table_schema, primary_key):
    """Create a merge statement to match the change
    data to the destination table data.
    """
    insert = ", ".join(destination_table_schema.keys())
    values = ", ".join([f"S.{x}" for x in destination_table_schema.keys()])
    set_keys = list(destination_table_schema.keys())
    set_keys.remove(primary_key)
    set_statement = ", ".join([f"T.{x} = S.{x}" for x in set_keys])
    merge_statement = f"""MERGE into {destination_table} as T
    using (select *
    from temp_{destination_table}_stream) AS S
    ON T.{primary_key} = S.{primary_key}
    when matched AND S.metadata$action = 'INSERT' AND S.metadata$isupdate
    THEN
    update set {set_statement}
    When matched
    And S.metadata$action = 'DELETE' THEN DELETE
    when not matched
    And S.metadata$action = 'INSERT' THEN
    INSERT ({insert})
    VALUES ({values});"""

    return merge_statement


class SnowflakeSink(DynamicSink):
    def __init__(
        self,
        user,
        password,
        account,
        warehouse,
        database,
        schema,
        source_table_schema,
        primary_key,
        destination_table,
    ):
        self.user = user
        self.password = password
        self.account = account
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.destination_table = destination_table
        self.primary_key = primary_key
        self.destination_table = destination_table
        self.destination_table_schema = source_table_schema
        self.stream_table_schema = source_table_schema | {
            "METADATA$ISUPDATE": "BOOLEAN",
            "METADATA$ACTION": "VARCHAR",
        }

    def build(self, worker_index, worker_count):
        return SnowflakePartition(
            self.user,
            self.password,
            self.account,
            self.warehouse,
            self.database,
            self.schema,
            self.destination_table,
            self.destination_table_schema,
            self.primary_key,
            self.stream_table_schema,
        )


class SnowflakePartition(StatelessSinkPartition):
    def __init__(
        self,
        user,
        password,
        account,
        warehouse,
        database,
        schema,
        destination_table,
        destination_table_schema,
        primary_key,
        stream_table_schema,
    ):
        self.conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema,
        )
        self.destination_table = destination_table
        self.destination_table_schema = destination_table_schema
        self.primary_key = primary_key
        self.stream_table_schema = stream_table_schema

        # create destination table if it doesn't exist
        columns__types = ", ".join(
            [
                " ".join(key__value)
                for key__value in self.destination_table_schema.items()
            ]
        )
        create = f"""CREATE TABLE IF NOT EXISTS {self.destination_table} ({columns__types});"""
        self.conn.cursor().execute(create)

    def write_batch(self, batch):
        """Takes the accumulated change data, reduces overwriting statements,
        formats the correct SQL statements and executes them in snowflake.
        """
        key, batch_events = batch[0]
        table_data = {}
        for event in batch_events:
            if event["op"] == "c":
                # create event
                stream_mods = {
                    "METADATA$ISUPDATE": False,
                    "METADATA$ACTION": "'INSERT'",
                }
                table_data[event["after"][self.primary_key]] = (
                    event["after"] | stream_mods
                )
            elif event["op"] == "u":
                # update event
                stream_mods = {"METADATA$ISUPDATE": True, "METADATA$ACTION": "'INSERT'"}
                table_data[event["after"][self.primary_key]] = (
                    event["after"] | stream_mods
                )
            elif event["op"] == "d":
                # delete event
                stream_mods = {"METADATA$ISUPDATE": True, "METADATA$ACTION": "'DELETE'"}
                table_data[event["before"][self.primary_key]] = (
                    event["before"] | stream_mods
                )

        print(table_data)
        query_string, insert_string = create_temp_table(
            table_data.values(), self.destination_table, self.stream_table_schema
        )
        self.conn.cursor().execute(query_string)
        self.conn.cursor().execute(insert_string)

        merge = merge_table(
            self.destination_table, self.destination_table_schema, self.primary_key
        )
        self.conn.cursor().execute(merge)

        drop = f"""DROP TABLE temp_{self.destination_table}_stream;"""
        self.conn.cursor().execute(drop)