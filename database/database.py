# This library allows us to talk to our database, we will store our temperature logs in here
import sqlite3
from logger import logger

DATABASE_NAME = './CodeClub.db'

# This is a mini library that will handle the interaction with the database for us
class DB:
    # This function will run once the first time we use this library
    # it creates a connection to the database and tries to set it up for us to use it
    def __init__(self):
        self._try_create_tables()

    def _connect(self):
        try:
            return sqlite3.connect(DATABASE_NAME)
        except Exception as e:
            logger.error(f"Failed to connect to SQlite: {e}")
            
    def _execute(self, command, parameters = None): 
        cursor: sqlite3.Cursor = None
        connection: sqlite3.Connection = None
        data = None

        try: 
            connection = sqlite3.connect(DATABASE_NAME)

            # Open the connection, this will let us run commands on the database using SQL
            cursor = connection.cursor()
            if parameters:
                data = cursor.execute(command, parameters)  
            else:
                data = cursor.execute(command)  

            data = data.fetchall()

            # save the changes we just made          
            connection.commit()

        except Exception as e:
            # If something doesn't work while running the command log it as an error
            logger.debug(f"Failed to run: {command}{parameters}")
            logger.error(f"Failed to run command: {e}")

        finally:
            # Whether it worked or not, we want to close our connection when we're done
            if cursor != None:
                cursor.close()
            
            if connection != None:
                connection.close()

            return data
            
    # This function will create the table in the database if it does not already exist
    def _try_create_tables(self):
        try:
            create_table_query = """
                CREATE TABLE IF NOT EXISTS environment_data (

                    -- This column is used by the database as a unique identifier, this is required for all tables
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    -- This column will be automatically populated with the date and time the records were created
                    timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP, 

                    -- This is used to identfy who the record belongs to 
                    user TEXT,

                    -- These will store the sensor data as numbers
                    lux NUMERIC,
                    pressure NUMERIC,
                    temperature NUMERIC,
                    humidity NUMERIC
                )
            """
            self._execute(create_table_query)
        except Exception as e: 
            logger.error(f"Failed to set up the database {e}")

    def get_data_for_user(self, user: str, page: int):
        if page > 0:
            page -= 1

        # This query asks the database to get 100 records 
        # Each record will contain timestamp, lux, pressure, temperature and humidity 
        get_data_query = """
        -- the columns we want to get
        SELECT timestamp, lux, pressure, temperature, humidity 

        -- the table we want to get it from 
        FROM environment_data 

        -- the filters we want to apply
        WHERE user = ? 

        -- sort by the time the records were created, newest records first
        ORDER BY timestamp DESC 

        -- the maximum amount of records to get
        LIMIT 50

        -- Skip the records we have already seen by multiplying the limit with the page number
        OFFSET 50 * ?
        """
        
        return self._execute(get_data_query, [(user), page])

    def write_data_for_user(self, user, lux, pressure, temp, humidity):
        try:
            logger.debug(f"Inserting user={user} lux={lux} pressure={pressure} temperature={temp} humidity={humidity}")
            
            # The question marks in this query will be replaced by 
            # (user, lux, pressure, temp, humidity) in that order
            # We do this to avoid a common security vulnerability called SQL Injection 
            # https://www.w3schools.com/sql/sql_injection.asp

            insert_data_query = """
            -- This tells the database that we want to write some data to the environment_data table
            INSERT INTO environment_data 

            -- The columns we want to update
            (user, lux, pressure, temperature, humidity) 

            -- The values we want to insert, see the comment above to find out why we don't put the actual values here 
            VALUES (?, ?, ?, ?, ?)
            """

            self._execute(insert_data_query, parameters=(user, lux, pressure, temp, humidity))
        except Exception as e:
            logger.error(f"Failed to insert data for {user}: {e}")

