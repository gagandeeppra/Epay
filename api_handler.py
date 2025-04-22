import requests
import json
import os

class APIHandler:
    def __init__(self):
        """
        Initialize the APIHandler with the API URL.
        """
        self.api_url = os.environ.get("API_URL")

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
                print(f"API call failed. Status code: {response.status_code}, Response: {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error occurred during API call: {e}")
            return []

    def _prepare_request_object(self, site_ids):
        """
        Prepare the request payload for the API call.

        Args:
            site_ids (list): List of site IDs to include in the request.

        Returns:
            dict: The request payload.
        """
        return {
            "siteIds": site_ids,
            "additionalData": "example_data"  # Replace with actual required fields
        }

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