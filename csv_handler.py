import csv
import os


class CSVHandler:
    def __init__(self, file_name=None):
        """
        Initialize the CSVHandler with the file name.
        Ensures the file is created inside the 'data' folder.
        """
        self.data_folder = "data"
        os.makedirs(
            self.data_folder, exist_ok=True
        )  # Create 'data' folder if it doesn't exist
        self.file_name = os.path.join(
            self.data_folder, file_name or os.environ.get("FILE_NAME")
        )
        if not self.file_name:
            raise ValueError(
                "File name must be provided either as an argument "
                "or through the FILE_NAME environment variable."
            )
        self.csv_fields = ["serial_number", "user_count"]  # Define header fields

    def write_csv(self, serial_number, user_count):
        """
        Append a row to the CSV file. If the file does not exist, it creates the file with headers.

        Args:
            serial_number (str): The serial number to write.
            user_count (int): The user count to write.
        """
        file_exists = os.path.exists(self.file_name)
        try:
            with open(self.file_name, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_fields)
                if not file_exists:  # Write header if the file does not exist
                    writer.writeheader()
                writer.writerow(
                    {"serial_number": serial_number, "user_count": user_count}
                )
        except Exception as e:
            print(f"Error writing to CSV file: {e}")

    def read_csv(self):
        """
        Read the CSV file and return a list of serial numbers.

        Returns:
            list: A list of serial numbers from the CSV file.
        """
        serial_numbers = []
        if os.path.exists(self.file_name):
            try:
                with open(self.file_name, "r", newline="") as f:
                    reader = csv.DictReader(f)
                    # Use a generator expression to efficiently extract serial numbers
                    serial_numbers = [row["serial_number"] for row in reader]
            except Exception as e:
                print(f"Error reading CSV file: {e}")
        else:
            print(f"CSV file '{self.file_name}' does not exist.")
        return serial_numbers
