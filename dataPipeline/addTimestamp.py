import pandas as pd
import sys
import numpy as np

def addTimestamp(csv_file_path):
    
    df = pd.read_csv(csv_file_path)
    df.insert(0, 'timestamp', np.arange(0, len(df) * 20, 20))
    df.to_csv(csv_file_path, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python addTimestamp.py <path_to_raw_csv>")
    else:
        addTimestamp(sys.argv[1])