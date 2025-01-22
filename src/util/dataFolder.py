import os
import pandas as pd


class DataFolder:
    def __init__(self, folderPath):
        self.folderPath = folderPath
        self.csv_files_list = self.find_all_csv_files()

    def find_all_csv_files(self):
        csvFiles = []

        for root, _, files in os.walk(self.folderPath):
            for file in files:
                if file.endswith(".csv"):
                    csvFiles.append(str(os.path.join(root, file)))
        return csvFiles

    def get_all_col_names(self):
        """
        Get the intersection of column names from all provided CSV files.

        Args:
            csv_files_list (list): List of CSV file paths.

        Returns:
            list: A list of column names that are common across all CSV files.
        """
        common_columns = None  # Initialize as None for the first file

        for file_path in self.csv_files_list:
            # Read only the header of the CSV file
            df = pd.read_csv(file_path, nrows=0)
            file_columns = set(df.columns.tolist())  # Get column names as a set

            if common_columns is None:
                # Initialize common_columns with the first file's columns
                common_columns = file_columns
            else:
                # Compute the intersection with the current file's columns
                common_columns &= file_columns

        # Return the intersection as a sorted list
        return sorted(common_columns) if common_columns else []

