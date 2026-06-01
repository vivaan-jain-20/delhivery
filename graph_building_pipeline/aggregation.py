import pandas as pd

def aggregate_edges(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups the pre-processed dataframe by source_center, destination_center, route_type, 
    and time_of_day. Calculates the median delay_ratio and total trips, then filters 
    out any corridors with fewer than 5 trips.
    """
    print("Aggregating edge traversals into corridors...")
    groupby_cols = ['source_center', 'destination_center', 'route_type', 'time_of_day']
    
    # Verify that the required columns are in the DataFrame
    for col in groupby_cols + ['delay_ratio', 'trip_uuid']:
        if col not in df.columns:
            raise KeyError(f"Required column '{col}' is missing from the DataFrame.")
            
    # Perform grouping and aggregation
    aggregated_edges = df.groupby(groupby_cols).agg(
        median_delay_ratio=('delay_ratio', 'median'),
        total_trips=('trip_uuid', 'count')
    ).reset_index()
    
    initial_corridors = len(aggregated_edges)
    
    # Filter out corridors with less than 5 trips to remove statistical noise
    aggregated_edges = aggregated_edges[aggregated_edges['total_trips'] >= 5].reset_index(drop=True)
    final_corridors = len(aggregated_edges)
    
    print(f"Aggregation completed: {initial_corridors} raw corridors aggregated -> {final_corridors} corridors with >= 5 trips.")
    return aggregated_edges
