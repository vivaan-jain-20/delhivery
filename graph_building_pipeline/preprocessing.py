import pandas as pd
import os

def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads delivery data from a CSV file.
    """
    print(f"Loading data from: {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    return pd.read_csv(file_path)

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs preprocessing on the loaded DataFrame:
    - Filters out rows with segment_osrm_time <= 0 to prevent division by zero.
    - Computes the delay_ratio = segment_actual_time / segment_osrm_time.
    """
    print("Starting preprocessing...")
    initial_rows = len(df)

    # Safeguard: Filter out invalid segment_osrm_time values
    invalid_osrm_mask = df['segment_osrm_time'] <= 0
    invalid_osrm_count = invalid_osrm_mask.sum()
    if invalid_osrm_count > 0:
        print(f"Filtering out {invalid_osrm_count} rows with segment_osrm_time <= 0 to prevent division-by-zero.")
        df = df[~invalid_osrm_mask].copy()
    
    # Calculate delay_ratio
    print("Calculating delay_ratio (segment_actual_time / segment_osrm_time)...")
    df['delay_ratio'] = df['segment_actual_time'] / df['segment_osrm_time']

    print(f"Preprocessing completed. Rows: {initial_rows} -> {len(df)}")
    return df
