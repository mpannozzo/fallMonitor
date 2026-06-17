import pandas as pd
import numpy as np
def extract_continuous_adl(csv_file_path, session_id):      
    output_file_path= f"labeled_adl_datasetedge{session_id}.csv"
    # 1. Load the raw daily activity data
    df = pd.read_csv(csv_file_path)
    df.insert(0, 'timestamp', np.arange(0, len(df) * 20, 20))
    # 2. Define the extraction parameters based on a 50 Hz sample rate
    points_per_window = 100  # 2 seconds of data
    step_size = 50           # 1 second of stagger (50% overlap)
    
    extracted_windows = []
    window_counter = 1
    
    # 3. Slide the window continuously across the entire dataframe
    # We use a standard for-loop with the step_size
    for start_idx in range(0, len(df) - points_per_window + 1, step_size):
        
        end_idx = start_idx + points_per_window
        
        # Extract the 2-second slice
        window_df = df.iloc[start_idx:end_idx].copy()
        
        # 4. Add ML Labeling Metadata
        window_df['Label'] = 0              # 0 = Not a Fall (ADL)
        window_df['Event_ID'] = session_id  # Groups this whole recording session
        window_df['Window_Number'] = window_counter
        
        extracted_windows.append(window_df)
        window_counter += 1
        
    # 5. Combine all slices and save
    if extracted_windows:
        final_dataset = pd.concat(extracted_windows, ignore_index=True)
        final_dataset.to_csv(output_file_path, index=False)
        print(f"Success! Processed ADL Session {session_id}.")
        print(f"Generated {len(extracted_windows)} total 2-second background windows.")
    else:
        print("Error: The dataset was too short to extract even a single 2-second window.")

# Example terminal usage via script:
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        input_csv = sys.argv[1]
        session_num = int(sys.argv[2])
        extract_continuous_adl(input_csv, session_num)
    else:
        print("Usage: python adl_extraction.py raw_adl_data.csv 100")