import requests
import json
import os


class APIHandler:
    def __init__(self):
        """
        Initialize the APIHandler with the API URL and employer ID.
        """
        self.api_url = os.environ.get("API_URL")
        self.employer_id = os.environ.get("EMPLOYER_ID")
        if not self.api_url or not self.employer_id:
            raise ValueError("API_URL and EMPLOYER_ID must be set as environment variables.")

    def fetch_device_serial_numbers(self, site_ids):
        """
        Fetch device serial numbers via an API call.

        Args:
            site_ids (list): List of site IDs to include in the API request.

        Returns:
            list: A list of device serial numbers if the API call is successful.
        """
        try:
            payload = self._prepare_request_object(site_ids)
            response = requests.post(self.api_url, json=payload)

            if response.status_code == 200:
                return self._extract_device_serial_numbers(response)
            else:
                print(
                    f"API call failed. Status code: {response.status_code}, "
                    f"Response: {response.text}"
                )
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error occurred during API call: {e}")
            return []

    def _extract_device_serial_numbers(self, response):
        """
        Extract device serial numbers from the API response.

        Args:
            response (requests.Response): The API response object.

        Returns:
            list: A list of device serial numbers.
        """
        try:
            data = response.json()
            employee_list = data.get("data", {}).get("employeeList", [])
            return [employee["employeeId"] for employee in employee_list]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing API response: {e}")
            return []

    def _prepare_employer_site_list(self, site_ids):
        """
        Prepare a list of employer site objects.

        Args:
            site_ids (list): List of site IDs.

        Returns:
            list: A list of employer site objects.
        """
        return [{"employerId": self.employer_id, "siteId": site_id} for site_id in site_ids]

    def _prepare_request_object(self, site_ids):
        """
        Prepare the request object for the API call.

        Args:
            site_ids (list): List of site IDs.

        Returns:
            dict: The request payload for the API call.
        """
        return {
            "employersSitesList": self._prepare_employer_site_list(site_ids),
            "lookBackWindowsInMinutes": -1,
            "managerIdList": [{"employeeId": 0}],
            "processId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        }