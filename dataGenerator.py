import sqlite3
import math
import random
from datetime import datetime, timedelta
from pathlib import Path


RECORDS = 288  # 24 hours at 5-minute intervals


def get_database():
    """Prompt for and validate the SQLite database path."""

    while True:
        database = input("Enter database filename/path, default CodeClub.db: ").strip()

        if not database:
            database = 'CodeClub.db'

        path = Path(database)

        # If a directory was entered rather than a file
        if path.exists() and path.is_dir():
            print("Error: The specified path is a directory, not a database file.")
            continue

        # Check that the parent directory exists
        parent = path.parent

        if not parent.exists():
            print(f"Error: Directory does not exist: {parent}")
            continue

        # Check that we can write to an existing database
        if path.exists():
            try:
                with open(path, "a"):
                    pass
            except PermissionError:
                print("Error: You do not have permission to write to this file.")
                continue

        return str(path)


def get_start_time():
    """Prompt for and validate the starting date/time."""
    while True:
        start_time = input(
            "Enter START_TIME (YYYY-MM-DD) or leave blank to generate for today: "
        ).strip()

        try:
            if not start_time: 
                start_time = datetime.today()
            
            timestamp = datetime.strptime(
                start_time,
                "%Y-%m-%d"
            )
        except ValueError:
            print(
                "Error: Invalid date/time. "
                "Please use YYYY-MM-DD HH:MM:SS."
            )
            continue

        # Make sure the time is on a 5-minute boundary.
        if timestamp.minute % 5 != 0 or timestamp.second != 0:
            print(
                "Error: START_TIME must be on a 5-minute boundary "
                "(e.g. 08:00:00, 08:05:00, 08:10:00)."
            )
            continue

        return timestamp


def generate_environment_data(timestamp):
    """Generate plausible forest environmental readings."""

    minutes = timestamp.hour * 60 + timestamp.minute

    # Approximate UK October daylight:
    # sunrise ~07:15, sunset ~18:20
    sunrise = 7 * 60 + 15
    sunset = 18 * 60 + 20

    # ---------------------------------------------------------
    # Light level (lux)
    # ---------------------------------------------------------

    if minutes < sunrise or minutes > sunset:
        # Very low light at night
        lux = random.uniform(0.1, 2.0)

    else:
        daylight_position = (
            (minutes - sunrise) / (sunset - sunrise)
        )

        # Smooth daylight curve
        lux = 5000 * math.sin(math.pi * daylight_position)

        # Forest canopy reduces available light
        lux *= random.uniform(0.7, 1.2)

        # Variable cloud cover
        lux *= random.uniform(0.4, 1.0)

        lux = max(lux, 1)

    # ---------------------------------------------------------
    # Temperature
    # ---------------------------------------------------------

    temperature = (
        10.5
        + 3.5 * math.sin(
            2 * math.pi * (minutes - 15 * 60) / (24 * 60)
        )
    )

    temperature += random.gauss(0, 0.3)

    # ---------------------------------------------------------
    # Humidity
    # ---------------------------------------------------------

    if sunrise <= minutes <= sunset:
        daylight_position = (
            (minutes - sunrise) / (sunset - sunrise)
        )

        humidity = (
            88
            - 22 * math.sin(math.pi * daylight_position)
        )
    else:
        humidity = 90

    humidity += random.gauss(0, 1.5)
    humidity = max(0, min(100, humidity))

    # ---------------------------------------------------------
    # Atmospheric pressure
    # ---------------------------------------------------------

    pressure = (
        1015
        + 2 * math.sin(2 * math.pi * minutes / (24 * 60))
        + random.gauss(0, 0.3)
    )

    return (
        round(lux, 2),
        round(pressure, 2),
        round(temperature, 2),
        round(humidity, 2),
    )


def main():

    print("Environmental Sensor Data Generator")
    print("------------------------------------")

    database = get_database()
    start_time = get_start_time()

    print()
    print(f"Database:   {database}")
    print(f"Start time: {start_time}")
    print(f"Records:    {RECORDS}")
    print(f"End time:   {start_time + timedelta(minutes=(RECORDS - 1) * 5)}")
    print()

    # ---------------------------------------------------------
    # Connect to database
    # ---------------------------------------------------------

    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS environment_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user TEXT,
                lux NUMERIC,
                pressure NUMERIC,
                temperature NUMERIC,
                humidity NUMERIC
            )
        """)

    except sqlite3.Error as error:
        print(f"Database error: {error}")
        return

    # ---------------------------------------------------------
    # Generate and insert records
    # ---------------------------------------------------------

    timestamp = start_time

    try:
        for _ in range(RECORDS):

            lux, pressure, temperature, humidity = (
                generate_environment_data(timestamp)
            )

            cursor.execute("""
                INSERT INTO environment_data
                    (
                        timestamp,
                        user,
                        lux,
                        pressure,
                        temperature,
                        humidity
                    )
                VALUES
                    (?, ?, ?, ?, ?, ?)
            """, (
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "demo",
                lux,
                pressure,
                temperature,
                humidity,
            ))

            timestamp += timedelta(minutes=5)

        conn.commit()

    except sqlite3.Error as error:
        conn.rollback()
        print(f"Error inserting data: {error}")
        conn.close()
        return

    conn.close()

    print(f"Successfully inserted {RECORDS} records.")


if __name__ == "__main__":
    main()