#!/usr/bin/env python
import openpyxl
import os

# Check the exported file
file_path = r"C:\Users\CDC.MIS.OJT\Downloads\Transmittals_20260210_113636.xlsx"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
else:
    try:
        workbook = openpyxl.load_workbook(file_path)
        worksheet = workbook.active
        
        print("Excel File Format Check:")
        print("=" * 80)
        print(f"File: {os.path.basename(file_path)}")
        print(f"Sheet: {worksheet.title}")
        print()
        
        # Get headers
        headers = []
        for col_num, cell in enumerate(worksheet[1], 1):
            if cell.value:
                headers.append(f"Col {col_num}: {cell.value}")
        
        print("Headers found:")
        for header in headers:
            print(f"  - {header}")
        print()
        
        # Get first few rows
        print("Data (first 3 rows):")
        print("-" * 80)
        for row_num, row in enumerate(worksheet.iter_rows(min_row=2, max_row=4, values_only=False), start=2):
            print(f"\nRow {row_num}:")
            for col_num, cell in enumerate(row, 1):
                if cell.value is not None:
                    print(f"  Col {col_num}: {cell.value}")
        
        print("\n" + "=" * 80)
        print("\nExpected Import Format:")
        print("  1. Reference Number")
        print("  2. Sender Email")
        print("  3. Recipient Name")
        print("  4. Recipient Email")
        print("  5. Recipient Company")
        print("  6. Origin Location")
        print("  7. Destination Location")
        print("  8. Description")
        print("  9. Status")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
