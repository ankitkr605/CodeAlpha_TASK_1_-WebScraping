import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

url = "https://www.contextures.com/xlSampleData01.html"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Try different approaches to find the correct table
data_table = None

# Method 1: Find by summary attribute
data_table = soup.find('table', attrs={'summary': 'Sample data for pivot tables'})

# Method 2: If not found, try to find the table that contains actual data headers
if data_table is None:
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        if rows:
            header_cells = rows[0].find_all(['th', 'td'])
            headers = [cell.get_text(strip=True) for cell in header_cells]
            # Look for the table with OrderDate, Region, Rep, Item columns
            if any('OrderDate' in str(header) or 'Region' in str(header) or 'Rep' in str(header) for header in headers):
                data_table = table
                print(f"Found data table using header matching")
                break

# Method 3: If still not found, use the largest table
if data_table is None:
    tables = soup.find_all('table')
    if tables:
        # Find the table with the most rows
        max_rows = 0
        for table in tables:
            row_count = len(table.find_all('tr'))
            if row_count > max_rows:
                max_rows = row_count
                data_table = table
        print(f"Using largest table with {max_rows} rows")

if data_table:
    rows = data_table.find_all('tr')

    header_cells = rows[0].find_all(['th', 'td'])
    headers = [cell.get_text(strip=True) for cell in header_cells]

    print(f"Found headers: {headers}")

    data = []
    for row in rows[1:]:
        cells = row.find_all(['th', 'td'])
        if len(cells) == len(headers):
            row_data = [cell.get_text(strip=True) for cell in cells]
            data.append(row_data)

    print(f"Extracted {len(data)} data rows")

    if data and headers:
        df = pd.DataFrame(data, columns=headers)

        print(f"\nDataFrame shape: {df.shape}")
        print("\nFirst 5 rows:")
        print(df.head())

        # Create filtered DataFrame
        columns_to_exclude = ['OrderDate', 'Region', 'Rep', 'Item', 'Units', 'UnitCost', 'Total']
        df_filtered = df.drop(columns=columns_to_exclude, errors='ignore')

        # Save both full and filtered datasets
        df.to_csv("custom_dataset.csv", index=False)
        df_filtered.to_csv("custom_dataset_filtered.csv", index=False)

        print(f"\n Full DataFrame saved as 'custom_dataset.csv' at {os.path.abspath('custom_dataset.csv')}")
        print(f" Filtered DataFrame saved as 'custom_dataset_filtered.csv' at {os.path.abspath('custom_dataset_filtered.csv')}")
        print(f"\nFiltered DataFrame shape: {df_filtered.shape}")
        print("\nFiltered DataFrame (first 5 rows):")
        print(df_filtered.head())
    else:
        print("No valid data extracted from the table")
else:
    print("Could not find any suitable data table on the webpage")
