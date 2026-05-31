import pandas as pd
import os

def clean_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_path = os.path.join(current_dir, "..", "delivery_data.csv")
    output_data_path = os.path.join(current_dir, "cleaned_delivery_data.csv")

    print(f"Loading raw data from: {os.path.abspath(raw_data_path)}")
    df = pd.read_csv(raw_data_path)
    initial_rows = len(df)
    print(f"Initial row count: {initial_rows}")

    # Define duration/time columns to check
    time_columns = [
        'actual_time', 
        'osrm_time', 
        'segment_actual_time', 
        'segment_osrm_time',
        'start_scan_to_end_scan'
    ]

    # 1. Remove rows with any negative time
    print("\n--- Step 1: Remove negative times ---")
    for col in time_columns:
        neg_count = (df[col] < 0).sum()
        print(f"Negative values in '{col}': {neg_count}")
    
    # Filter out rows where any of the time columns are negative
    condition_negative = (df[time_columns] < 0).any(axis=1)
    df = df[~condition_negative]
    print(f"Rows remaining after removing negative times: {len(df)}")

    # 2. Remove rows with any zero time
    print("\n--- Step 2: Remove zero times ---")
    for col in time_columns:
        zero_count = (df[col] == 0).sum()
        print(f"Zero values in '{col}': {zero_count}")
        
    # Filter out rows where any of the time columns are zero
    condition_zero = (df[time_columns] == 0).any(axis=1)
    df = df[~condition_zero]
    print(f"Rows remaining after removing zero times: {len(df)}")

    # 3. Remove rows with segment factor greater than 30
    print("\n--- Step 3: Remove segment factor > 30 ---")
    high_factor_count = (df['segment_factor'] > 30).sum()
    print(f"Rows with segment_factor > 30: {high_factor_count}")
    
    df = df[df['segment_factor'] <= 30]
    print(f"Rows remaining after removing segment_factor > 30: {len(df)}")

    # 4. Drop rows with missing names and extract state names
    print("\n--- Step 4: Drop missing names and extract state names ---")
    null_source_before = df['source_name'].isnull().sum()
    null_dest_before = df['destination_name'].isnull().sum()
    print(f"Null source_name count before: {null_source_before}")
    print(f"Null destination_name count before: {null_dest_before}")

    # Drop any rows with null source_name or destination_name
    df = df.dropna(subset=['source_name', 'destination_name'])
    print(f"Rows remaining after dropping null locations: {len(df)}")

    # Extract state names (anything inside parentheses at the end of the string)
    df['source_state'] = df['source_name'].str.extract(r'\(([^)]+)\)$')
    df['destination_state'] = df['destination_name'].str.extract(r'\(([^)]+)\)$')

    # Clean the source_name and destination_name by removing the trailing state suffix
    df['source_name'] = df['source_name'].str.replace(r'\s*\([^)]+\)$', '', regex=True)
    df['destination_name'] = df['destination_name'].str.replace(r'\s*\([^)]+\)$', '', regex=True)

    print(f"Null source_name count after: {df['source_name'].isnull().sum()}")
    print(f"Null destination_name count after: {df['destination_name'].isnull().sum()}")
    print(f"Unique source states extracted: {df['source_state'].nunique()}")
    print(f"Unique destination states extracted: {df['destination_state'].nunique()}")

    # 5. Time parsing, binning, and column dropping
    print("\n--- Step 5: Time parsing, binning, and column dropping ---")
    print("Parsing trip_creation_time to datetime...")
    df['trip_creation_time'] = pd.to_datetime(df['trip_creation_time'])
    
    print("Extracting hour and binning to time_of_day...")
    hours = df['trip_creation_time'].dt.hour
    df['time_of_day'] = pd.cut(
        hours,
        bins=[0, 6, 12, 18, 24],
        labels=['Night', 'Morning', 'Afternoon', 'Evening'],
        right=False,
        include_lowest=True
    )
    
    print("Dropping cutoff columns (is_cutoff, cutoff_factor, cutoff_timestamp)...")
    df = df.drop(columns=['is_cutoff', 'cutoff_factor', 'cutoff_timestamp'])

    # Summary
    final_rows = len(df)
    removed_rows = initial_rows - final_rows
    print("\n--- Summary ---")
    print(f"Initial rows: {initial_rows}")
    print(f"Final cleaned rows: {final_rows}")
    print(f"Total rows removed: {removed_rows} ({removed_rows / initial_rows * 100:.2f}%)")

    # Save cleaned data
    print(f"\nSaving cleaned dataset to: {os.path.abspath(output_data_path)}")
    df.to_csv(output_data_path, index=False)
    print("Cleaned dataset saved successfully.")

if __name__ == "__main__":
    clean_data()
