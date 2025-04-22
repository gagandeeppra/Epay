import os
from pymssql import _mssql
import requests

def execute_stored_proc(server, user, password, database):
    conn = _mssql.connect(server=server, user=user, password=password, database=database)
    conn.execute_query('getasset')
    site_group_list = []
    for row in conn:
        print(f"AssetID={row['AssetID']}, SerialNo={row['SerialNo']}, SiteID={row['SiteID']}, SiteGroupId={row['SiteGroupId']}")
        site_id = row['SiteID']
        site_group_id = row['SiteGroupId']
        if site_id == 0 and site_group_id is None:
            save_to_db(site_id)
        else:
            conn.execute_query(f'usp_NEXD_GetSiteGroupSites @sitegroupID={site_group_id}')
            for row in conn:
                site_group_list.append(row["siteid"])
            save_to_db(site_group_list)

def prepare_employer_site_list(list_site_id):
    employers_site_list  = []
    for site_id in list_site_id:
        employer_site_obj = {
            "employerId" : EMPLOYER_ID,
            "siteId": site_id
        }
        employers_site_list.append(employer_site_obj)
    return employers_site_list

def prepare_request_object(list_site_id):    
    request_object = {
                        "employersSitesList": prepare_employer_site_list(list_site_id),
                        "lookBackWindowsInMinutes": 0,
                        "managerIdList": [
                            {
                            "employeeId": 0
                            }
                        ],
                        "processId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                    }
    return request_object

def save_to_db(list_site_id):
    try:
        # Make a call to POST to save in the DB
        response = requests.post(API_URL, json= prepare_request_object(list_site_id))
        if response.status_code == "200":
            print("Insert Successful")
    except requests.exceptions.RequestException as e :
        print(f"Some Error Occurred:{e}")


if __name__ == "__main__":
    # Define the database connection parameters
    SERVER_NAME = os.environ.get("SERVER_NAME")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    USER = os.environ.get("USER")  # SQL Server login username
    PASSWORD = os.environ.get("PASSWORD") # SQL Server login password
    PROC_NAME = os.environ.get("PROC_NAME")
    EMPLOYER_ID = int(os.environ.get("EMPLOYER_ID"))
    API_URL = os.environ.get("API_URL")
    execute_stored_proc(SERVER_NAME,USER,PASSWORD,DATABASE_NAME)