import os
from sqlalchemy import create_engine


class DatabaseUpdater:
    def __init__(self, server_name, database_name, user, password):
        """
        Initialize the DatabaseUpdater with connection parameters.
        """
        self.server_name = server_name
        self.database_name = database_name
        self.user = user
        self.password = password
        self.engine = self._create_engine()

    def _create_engine(self):
        """
        Create a SQLAlchemy engine for connecting to the database.
        """
        connection_string = (
            f"mssql+pyodbc://{self.user}:{self.password}@{self.server_name}/{self.database_name}"
            f"?driver=ODBC+Driver+17+for+SQL+Server"
        )
        return create_engine(connection_string, fast_executemany=True)

    def fetch_assest(self):
        """
        Update product price and quantity in the database.
        """
        connection = self.engine.raw_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "EXEC getasset ?",
                [employer_id],
            )
            connection.commit()
        except Exception as e:
            print(f"Error executing SP: {e}")
        finally:
            cursor.close()
            



if __name__ == "__main__":
    # Define the database connection parameters
    SERVER_NAME = os.environ.get("SERVER_NAME")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    USER = os.environ.get("USER")  # SQL Server login username
    PASSWORD = os.environ.get("PASSWORD") # SQL Server login password
    PROC_NAME = "getassest"

    # Create an instance of DatabaseUpdater and process the data
    db_updater = DatabaseUpdater(SERVER_NAME, DATABASE_NAME, USER, PASSWORD)
    db_updater.process_data()