import pandas as pd
import os

# 1. Put the exact name of your large ADL file here
input_file = 'labeled_fall_dataset_edge.csv' 

# 2. Name the folder where you want the slices to go
output_folder = '_chunks1'

# Check if the folder exists, and create it if it doesn't
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created new folder: {output_folder}/")

# Load the large dataset
df = pd.read_csv(input_file)

# 50Hz * 10 seconds = 500 rows per chunk
rows_per_chunk = 100 

print(f"Loaded {len(df)} rows. Slicing into 10-second chunks...")

# Loop through the data and slice it up
chunk_count = 0
for i in range(0, len(df), rows_per_chunk):
    chunk = df.iloc[i : i + rows_per_chunk]
    
    # Only save it if it's a complete 10-second window
    if len(chunk) == rows_per_chunk:
        # Construct the exact file path (e.g., adl_chunks/adl_10sec_chunk_0.csv)
        filename = os.path.join(output_folder, f'fall_chunk_{chunk_count}.csv')
        chunk.to_csv(filename, index=False)
        chunk_count += 1

print(f"Success! Saved {chunk_count} files neatly into the '{output_folder}' folder.")

