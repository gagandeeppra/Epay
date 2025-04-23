import os
from pymssql import _mssql
from csv_handler import CSVHandler
from api_handler import APIHandler
import time

class DatabaseHandler:
    def __init__(self, server, user, password, database, api_url, table_name):
        """
        Initialize the DatabaseHandler with connection parameters and configurations.
        """
        self.asset_id = 0
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.api_url = api_url
        self.api_serial_number_list = []
        self.mqtt_serial_number_list = CSVHandler().read_csv()
        self.table_name = table_name
        self._connection_instance = None

    def get_db_connection(self):
        """
        Get a singleton database connection.

        Returns:
            _mssql.Connection: A singleton database connection instance.
        """
        if self._connection_instance is None:
            self._connection_instance = _mssql.connect(
                server=self.server,
                user=self.user,
                password=self.password,
                database=self.database
            )
        return self._connection_instance

    def execute_stored_proc(self, proc_name):
        """
        Execute a stored procedure and process the results.
        """
        try:
            conn = self.get_db_connection()
            conn.execute_query(proc_name)
            rows = list(conn)
            for row in rows:
                self._process_row(conn, row)
        except _mssql.MssqlDatabaseException as e:
            print(f"Database error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def _process_row(self, conn, row):
        """
        Process a single row from the stored procedure result.
        """
        self.asset_id = row["SerialNo"]
        site_id = row['SiteID']
        site_group_id = row['SiteGroupId']

        if site_id == 0 and site_group_id is None:
            self.api_serial_number_list = APIHandler().fetch_device_serial_numbers([site_id])
        else:
            site_group_list = self._get_site_group_sites(conn, site_group_id)
            self.api_serial_number_list = APIHandler().fetch_device_serial_numbers(site_group_list)
        
        self._save_to_db()

    def _get_site_group_sites(self, conn, site_group_id):
        """
        Retrieve site group sites using a stored procedure.
        """
        site_group_list = []
        conn.execute_query(f'usp_NEXD_GetSiteGroupSites @sitegroupID={site_group_id}')
        for row in conn:
            site_group_list.append(row["siteid"])
        return site_group_list

    def _save_to_db(self):
        """
        Save data to the table.
        """
        try:
            conn = self.get_db_connection()
            difference = len(self.mqtt_serial_number_list) - len(self.api_serial_number_list)
            sql = (
                f"INSERT INTO {self.table_name} "
                f"(SerialNo, MQTTEmployeeno, DatabaseEmoNo, Diff) "
                f"VALUES ({self.asset_id}, {len(self.mqtt_serial_number_list)}, "
                f"{len(self.api_serial_number_list)}, {difference})"
            )
            conn.execute_query(sql)
        except _mssql.MssqlDatabaseException as e:
            print(f"Database error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    start_time = time.time()
    # Load configuration from environment variables
    SERVER_NAME = os.environ.get("SERVER_NAME")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    USER = os.environ.get("USER")
    PASSWORD = os.environ.get("PASSWORD")
    PROC_NAME = os.environ.get("PROC_NAME", "getasset")
    API_URL = os.environ.get("API_URL")
    TABLE_NAME = os.environ.get("TABLE_NAME")

    # Validate required configurations
    if not all([SERVER_NAME, DATABASE_NAME, USER, PASSWORD, API_URL, TABLE_NAME]):
        print("Missing required environment variables. Please check your configuration.")
    else:
        # Initialize and execute the database handler
        db_handler = DatabaseHandler(
            server=SERVER_NAME,
            user=USER,
            password=PASSWORD,
            database=DATABASE_NAME,
            api_url=API_URL,
            table_name=TABLE_NAME
        )
        db_handler.execute_stored_proc(PROC_NAME)
        end_time = time.time()
        print(f"Script takes:{end_time-start_time} seconds")