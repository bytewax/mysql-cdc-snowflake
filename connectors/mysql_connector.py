from datetime import datetime
from random import randint
from typing import Iterable, Optional

from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import DeleteRowsEvent, UpdateRowsEvent, WriteRowsEvent
from bytewax.inputs import FixedPartitionedSource, StatefulSourcePartition


def convert_event_to_dict(schema, table, event):
    events = []
    for row in event.rows:
        print(row)
        if isinstance(event, WriteRowsEvent):
            op_type = 'c'  # Assuming 'c' stands for create/insert
            before_values = None
            after_values = row.get("values", None)
        elif isinstance(event, UpdateRowsEvent):
            op_type = 'u'  # Assuming 'u' stands for update
            before_values = row.get("before_values", None)
            after_values = row.get("after_values", None)
        elif isinstance(event, DeleteRowsEvent):
            op_type = 'd'  # Assuming 'd' stands for delete
            before_values = row.get("values", None)
            after_values = None
        else:
            return None  # Non-row events are not handled

        events.append((f"{schema}:{table}",{
                "before": before_values,
                "after": after_values,
                "op": op_type,
                "ts_ms": event.timestamp * 1000,  # Convert to milliseconds
                "transaction": None,  # You may need to handle transaction logic based on your needs
        }))
    return events


class MySQLBinLogSource(FixedPartitionedSource):
    def __init__(self, mysql_settings):
        self.mysql_settings = mysql_settings

    def list_parts(self):
        return["single-part"]
    
    def build_part(self, _now, _for_key, _resume_state):
        return MySQLBinLogPartition(self.mysql_settings)
    
class MySQLBinLogPartition(StatefulSourcePartition):
    def __init__(self, mysql_settings): 
        self.stream = BinLogStreamReader(
            connection_settings=mysql_settings,
            server_id= randint(0,10000),  # Server ID must be unique for each replication slave
            only_events=[DeleteRowsEvent, UpdateRowsEvent, WriteRowsEvent],
            blocking=True,
            resume_stream=True
        )

    def next_batch(self) -> Iterable[tuple]:
        binlogevent = self.stream.fetchone()
        if binlogevent is None:
            return []  # or return an appropriate value indicating no events
        schema = binlogevent.schema
        table = binlogevent.table
        batch = convert_event_to_dict(schema, table, binlogevent)
        return [batch]
    
    def snapshot(self) -> None:
        return None
    
    def close(self):
        self.stream.close()