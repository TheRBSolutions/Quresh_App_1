import pandas as pd
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def process_excel_file(excel_file):
    # Read the Excel file, skipping the header row
    df = pd.read_excel(excel_file, header=None)
    
    # Log the column names for debugging
    logger.info(f"Columns in the Excel file: {df.columns.tolist()}")

    json_data = []
    extracted_images = []
    
    # Find the row where 'No.' or 'Number' column has a value of 1
    start_row = None
    for index, row in df.iterrows():
        if 1 in row.values:
            start_row = index
            break
    
    if start_row is None:
        logger.error("Could not find a row starting with 1 in the Excel file")
        raise ValueError("The Excel file does not contain a row starting with 1")

    # Slice the dataframe to start from the identified row
    df = df.iloc[start_row:]
    
    # Reset the index to start from 0
    df = df.reset_index(drop=True)
    
    # Identify the price column (assuming it's the last column)
    price_column = df.columns[-1]
    
    for index, row in df.iterrows():
        # Create 'No.' based on the row index (adding 1 to start from 1)
        item_no = index + 1
        
        # Combine all columns except the last one (price) into 'Information'
        information = " ".join(str(val) for val in row[1:-1] if pd.notna(val))
        
        # Extract price from the last column
        price = row[price_column] if pd.notna(row[price_column]) else 0.00
        
        item_data = {
            'No': item_no,
            'Information': information,
            'Price': price
        }
        
        # Use the correct image naming convention
        image_filename = f"{item_no}.png"
        image_path = os.path.join('excel_images', image_filename)
        item_data['Image'] = image_path
        
        json_data.append(item_data)
        extracted_images.append(image_path)
    
    return json_data, extracted_images