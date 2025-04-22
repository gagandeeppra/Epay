import os
import requests
from pymssql import _mssql
import json


class DatabaseProcessor:
    def __init__(self, server, user, password, database, employer_id, api_url):
        """
        Initialize the DatabaseProcessor with connection parameters and configurations.
        """
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.employer_id = employer_id
        self.api_url = api_url

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
        print(f"AssetID={row['AssetID']}, SerialNo={row['SerialNo']}, SiteID={row['SiteID']}, SiteGroupId={row['SiteGroupId']}")
        site_id = row['SiteID']
        site_group_id = row['SiteGroupId']

        if site_id == 0 and site_group_id is None:
            self._save_to_db([site_id])
        else:
            site_group_list = self._get_site_group_sites(conn, site_group_id)
            self._save_to_db(site_group_list)

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

    def _save_to_db(self, site_ids):
        """
        Save data to the database via an API call.
        """
        try:
            response = requests.post(self.api_url, json=self._prepare_request_object(site_ids))
            if response.status_code == 200:
                employeeList = json.loads(response.text)["data"]["employeeList"]
                device_serial_number  = [employee["employeeId"] for employee in employeeList]
                #Perform csv and api comparison here
                # if not match insert into new table
            else:
                print(f"Failed to insert data. Status code: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error occurred during API call: {e}")


if __name__ == "__main__":
    # Load configuration from environment variables
    SERVER_NAME = os.environ.get("SERVER_NAME")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    USER = os.environ.get("USER")
    PASSWORD = os.environ.get("PASSWORD")
    PROC_NAME = os.environ.get("PROC_NAME", "getasset")
    EMPLOYER_ID = int(os.environ.get("EMPLOYER_ID", 0))
    API_URL = os.environ.get("API_URL")

    # Validate required configurations
    if not all([SERVER_NAME, DATABASE_NAME, USER, PASSWORD, EMPLOYER_ID, API_URL]):
        print("Missing required environment variables. Please check your configuration.")
    else:
        # Initialize and execute the database processor
        db_processor = DatabaseProcessor(SERVER_NAME, USER, PASSWORD, DATABASE_NAME, EMPLOYER_ID, API_URL)
        db_processor.execute_stored_proc(PROC_NAME)