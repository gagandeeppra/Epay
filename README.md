# Epay Project

This project is designed to handle MQTT communication, process device data, and manage CSV and API operations. It consists of multiple modules that work together to achieve the desired functionality.

## Folder Structure

## Modules

### 1. `main.py`
The main entry point of the application. It initializes the MQTT communication and processes incoming messages.

- **Features**:
  - Subscribes to MQTT topics.
  - Publishes requests to devices.
  - Processes responses and writes data to a CSV file.

### 2. `mqtt_helper.py`
Handles MQTT communication using the `paho-mqtt` library.

- **Features**:
  - Connects to the MQTT broker.
  - Subscribes to topics.
  - Publishes messages.
  - Processes incoming MQTT messages.

### 3. `csv_handler.py`
Manages CSV file operations such as creating, writing, and reading CSV files.

- **Features**:
  - Creates a CSV file with headers if it doesn't exist.
  - Appends rows to the CSV file.
  - Reads serial numbers from the CSV file.

### 4. `api_handler.py`
Handles API interactions to fetch device serial numbers.

- **Features**:
  - Sends POST requests to the API.
  - Extracts device serial numbers from the API response.
  - Handles errors during API calls.

## Setup

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package manager)

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Epay

2. Install dependencies:
    ```bash
    pip install -r requirements.txt

3. Set up environment variables: Create a .env file or export the following variables:
    ```
    export API_URL=xxxxxxxx
    export EMPLOYER_ID=xxxxxxxx
    export FILE_NAME=xxxxxxxx
    export SERVER_NAME=xxxxxxxx
    export DATABASE_NAME=xxxxxxxx
    export USER=xxxxxxxx
    export PASSWORD=xxxxxxxx
    export PROC_NAME="getasset"
    export EMPLOYER_ID=xxxxxxxx
    export API_URL = "https://nexd.epaysystems.com/employee/v1/TimeClockEmployee/Employees"
    export FILE_NAME="mqtt_extract.csv"
    export TABLE_NAME="SecureIDClockVarification"

### Usage
1. Run the Application: Execute the main.py file:
    ```bash
    python main.py -pf <product-flavor>
    python db_handler.py

2. CSV Operations:
    The csv_handler.py module automatically creates and updates the CSV file with device data.

3.API Operations:
    The api_handler.py module fetches device serial numbers from the API.

### Dependencies:
    The project uses the following Python libraries:
    *  paho-mqtt: For MQTT communication.
    *  requests: For API interactions.
    *  csv: For CSV file operations.
    *  pymssql: For SQL Server Operations.



### Contributing
Contributions are welcome! Please follow these steps:

    - Fork the repository.
    - Create a new branch for your feature or bug fix.
    - Commit your changes and push the branch.
    - Submit a pull request.

### License
This project is licensed under the MIT License. See the LICENSE file for details.

Contact
For any questions or issues, please contact:

* Name: Gagan
* Email: [gagandeep.pratihar@prismhr.com]