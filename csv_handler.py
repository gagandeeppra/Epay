import csv
import os

class CSVHandler:
    def __init__(self, file_name=None):
        """
        Initialize the CSVHandler with the file name.
        """
        self.file_name = file_name or os.environ.get("FILE_NAME")
        if not self.file_name:
            raise ValueError("File name must be provided either as an argument or through the FILE_NAME environment variable.")

    def write_csv(self, serial_number, user_count):
        """
        Append a row to the CSV file.
        """
        try:
            with open(self.file_name, 'a', newline='') as f:
                csv_fields = ['serial_number', 'user_count']
                writer = csv.DictWriter(f, fieldnames=csv_fields)
                writer.writerow({"serial_number": serial_number, "user_count": user_count})
        except Exception as e:
            print(f"Error writing to CSV file: {e}")

    def create_csv(self):
        """
        Create the CSV file with headers if it does not exist.
        """
        if not os.path.exists(self.file_name):
            try:
                with open(self.file_name, 'w', newline='') as f:
                    csv_fields = ['serial_number', 'user_count']
                    writer = csv.DictWriter(f, fieldnames=csv_fields)
                    writer.writeheader()
            except Exception as e:
                print(f"Error creating CSV file: {e}")