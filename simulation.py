import pymysql
import random
from datetime import datetime, timedelta

# MySQL connection settings
config = {
    "host": "localhost",
    "user": "root",
    "password": "example",
    "db": "bytewax",
    "charset": 'utf8mb4',
    "cursorclass": pymysql.cursors.DictCursor
}

def create_trips_table_if_not_exists(connection):
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Trips (
                TRIPID INT PRIMARY KEY,
                DRIVERID INT,
                TIMECOMPLETED TIMESTAMP NULL
            );
        """)
    connection.commit()


def simulate_trips(connection, num_trips=100):
    with connection.cursor() as cursor:
        for i in range(1, num_trips + 1):
            driver_id = random.randint(1, 10)  # Assuming driver IDs between 1 and 10
            # Insert the trip
            sql_insert = "INSERT INTO Trips (TRIPID, DRIVERID, TIMECOMPLETED) VALUES (%s, %s, %s)"
            cursor.execute(sql_insert, (i, driver_id, None))

            # Decide to either complete or delete the trip
            action = random.choice(["complete", "delete"])
            if action == "complete":
                completion_time = datetime.now() + timedelta(days=random.randint(1, 30))  # Random completion date within the next 30 days
                sql_update = "UPDATE Trips SET TIMECOMPLETED = %s WHERE TRIPID = %s"
                cursor.execute(sql_update, (completion_time, i))
            elif action == "delete":
                # To ensure realistic simulation, we might delay deletion to a separate step after initial setup
                continue  # For now, do nothing, and we'll delete some trips in a separate step

    connection.commit()

def delete_random_trips(connection, num_trips=100):
    with connection.cursor() as cursor:
        # Randomly select trips to delete, not exceeding 30% of the total
        trips_to_delete = random.sample(range(1, num_trips + 1), k=int(num_trips * 0.3))
        for trip_id in trips_to_delete:
            sql_delete = "DELETE FROM Trips WHERE TRIPID = %s"
            cursor.execute(sql_delete, (trip_id,))
    connection.commit()

def main():
    connection = pymysql.connect(**config)
    try:
        create_trips_table_if_not_exists(connection)
        simulate_trips(connection)
        delete_random_trips(connection)  # Separately handle deletions to ensure some completed trips are also deleted
    finally:
        connection.close()

if __name__ == "__main__":
    main()