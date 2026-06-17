import pandas as pd
import sys
import numpy as np

def extract_staggered_falls(csv_file_path, output_file_path="labeled_fall_dataset_edge.csv"):
    # 1. Load the raw data
    df = pd.read_csv(csv_file_path)
    df.insert(0, 'timestamp', np.arange(0, len(df) * 20, 20))
    # 2. Define the extraction parameters based on a 50 Hz sample rate
    points_per_window = 100  # 2 seconds of data
    step_size = 5            # 0.1 seconds of stagger
    num_windows = 10         # Total windows per event
    
    # 3. Edge Detection: Find ONLY the exact moments the indicator flips from 0 to 1.
    # This prevents the script from triggering multiple times while the button is held down.
    trigger_indices = df.index[(df['Fall_Indicator'] == 1) & (df['Fall_Indicator'].shift(1) == 0)].tolist()
    
    extracted_windows = []
    event_counter = 1
    
    for trigger_idx in trigger_indices:
        # 4. Generate the 10 staggered windows for this single fall event
        for i in range(num_windows):
            # Calculate the start and end row for this specific slice
            start_idx = trigger_idx + (i * step_size)
            end_idx = start_idx + points_per_window
            
            # 5. Boundary check to ensure we don't read past the end of the CSV
            if end_idx <= len(df):
                # Slice the dataframe
                window_df = df.iloc[start_idx:end_idx].copy()
                
                # Add labeling metadata so you can group them later during training
                window_df['Event_ID'] = event_counter
                window_df['Window_Number'] = i + 1
                
                extracted_windows.append(window_df)
            else:
                print(f"Warning: File ended before finishing Event {event_counter}, Window {i+1}")
                
        event_counter += 1
        
    # 6. Combine all slices and save
    if extracted_windows:
        final_dataset = pd.concat(extracted_windows, ignore_index=True)
        final_dataset.to_csv(output_file_path, index=False)
        print(f"Success! Processed {event_counter - 1} physical fall events.")
        print(f"Generated {len(extracted_windows)} total 2-second training windows.")
    else:
        print("No fall triggers (0 to 1 transitions) were found in the dataset.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extractFallEvents.py <path_to_raw_csv>")
    else:
        extract_staggered_falls(sys.argv[1])