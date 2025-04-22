import os
from pymssql import _mssql
from csv_handler import CSVHandler
from api_handler import APIHandler


class DatabaseProcessor:
    def __init__(self, server, user, password, database, employer_id, api_url, table_name):
        """
        Initialize the DatabaseProcessor with connection parameters and configurations.
        """
        self.asset_id = 0
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.employer_id = employer_id
        self.api_url = api_url
        self.api_serial_number_list = []
        self.mqtt_serial_number_list = []
        self.table_name = table_name

    def execute_stored_proc(self, proc_name):
        """
        Execute a stored procedure and process the results.
        """
        try:
            with _mssql.connect(server=self.server, user=self.user, password=self.password, database=self.database) as conn:
                conn.execute_query(proc_name)
                for row in conn:
                    self._process_row(conn, row)
        except _mssql.MssqlDatabaseException as e:
            print(f"Database error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def _process_row(self, conn, row):
        """
        Process a single row from the stored procedure result.
        """
        self.asset_id = row["AssetID"]
        site_id = row['SiteID']
        site_group_id = row['SiteGroupId']

        if site_id == 0 and site_group_id is None:
            self.api_serial_number_list = APIHandler().fetch_device_serial_numbers([site_id])
        else:
            site_group_list = self._get_site_group_sites(conn, site_group_id)
            self.api_serial_number_list = APIHandler().fetch_device_serial_numbers(site_group_list)

    def _get_site_group_sites(self, conn, site_group_id):
        """
        Retrieve site group sites using a stored procedure.
        """
        site_group_list = []
        conn.execute_query(f'usp_NEXD_GetSiteGroupSites @sitegroupID={site_group_id}')
        for row in conn:
            site_group_list.append(row["siteid"])
        return site_group_list

    def _prepare_employer_site_list(self, site_ids):
        """
        Prepare a list of employer site objects.
        """
        return [{"employerId": self.employer_id, "siteId": site_id} for site_id in site_ids]

    def _prepare_request_object(self, site_ids):
        """
        Prepare the request object for the API call.
        """
        return {
            "employersSitesList": self._prepare_employer_site_list(site_ids),
            "lookBackWindowsInMinutes": -1,
            "managerIdList": [{"employeeId": 0}],
            "processId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        }

    def _save_to_db(self):
        """
        Save data to the table
        """
        try:
            with _mssql.connect(server=self.server, user=self.user, password=self.password, database=self.database) as conn:
                cursor = conn.cursor()
                # Fetch API Device Number Count
                # Fetch MQTT Device Number Count
                # Diff
                difference = len(self.mqtt_serial_number_list) - len(self.api_serial_number_list)
                sql = f"INSERT INTO {self.table_name} (SerialNo, MQTTEmployeeno, DatabaseEmoNo, Diff) VALUES ({self.asset_id}, {self.mqtt_serial_number_list}, {self.api_serial_number_list}, {difference})"
                values = (1, 'Alice', 30)
                cursor.execute(sql, values)
                    # you must call commit() to persist your data if you don't set autocommit to True
                conn.commit()
        except _mssql.MssqlDatabaseException as e:
            print(f"Database error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Load configuration from environment variables
    SERVER_NAME = os.environ.get("SERVER_NAME")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    USER = os.environ.get("USER")
    PASSWORD = os.environ.get("PASSWORD")
    PROC_NAME = os.environ.get("PROC_NAME", "getasset")
    EMPLOYER_ID = int(os.environ.get("EMPLOYER_ID", 0))
    API_URL = os.environ.get("API_URL")
    TABLE_NAME = os.environ.get("TABLE_NAME")

    # Validate required configurations
    if not all([SERVER_NAME, DATABASE_NAME, USER, PASSWORD, EMPLOYER_ID, API_URL]):
        print("Missing required environment variables. Please check your configuration.")
    else:
        # Initialize and execute the database processor
        db_processor = DatabaseProcessor(SERVER_NAME, USER, PASSWORD, DATABASE_NAME, EMPLOYER_ID, API_URL, TABLE_NAME)
        db_processor.execute_stored_proc(PROC_NAME)