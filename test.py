import pandas as pd

def list_sheet_names(filename):
    """
    List all sheet names in the Excel file.
    """
    excel_file = pd.ExcelFile(filename)
    return excel_file.sheet_names

# Use the function to list the sheet names
filename = "Mappe1.xlsx"  # Copy file path
print("Available sheet names:", list_sheet_names(filename))
