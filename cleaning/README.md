# Data Cleaning Component

This folder contains scripts to parse and clean Delhivery's raw delivery segment dataset, filtering out anomalies and restructuring it for graph construction.

## File Overview

* **`clean.py`**: The cleaning script. Reads raw data from the parent directory (`../delivery_data.csv`) and outputs the cleaned dataset locally (`cleaned_delivery_data.csv`).
* **`cleaned_delivery_data.csv`** *(ignored by git)*: The generated high-quality cleaned dataset used by the downstream pipeline.

---

## Cleaning Operations Performed

The cleaning process executes the following steps:

1. **Negative Time Filtering**:
   * Scans and removes rows containing negative duration times in `actual_time`, `osrm_time`, `segment_actual_time`, `segment_osrm_time`, and `start_scan_to_end_scan`.
2. **Zero Time Filtering**:
   * Removes rows where transit durations are exactly `0` minutes, preventing downstream division-by-zero errors.
3. **Outlier Filtering**:
   * Filters out rows where `segment_factor` exceeds 30 (extreme outliers that skew median calculations).
4. **Location Validation**:
   * Drops rows with missing (`NaN`) `source_name` or `destination_name` values.
5. **State & Label Cleanups**:
   * Extracts the state name (e.g. `Gujarat`) from parentheses and saves it as new features `source_state` and `destination_state`.
   * Strips parenthesized state suffixes from `source_name` and `destination_name` to keep labeling clean.
6. **Time Parsing & Binning**:
   * Parses `trip_creation_time` to datetime.
   * Extracts the hour and bins it into a categorical `time_of_day` column:
     * `'Night'` (0-6 hours)
     * `'Morning'` (6-12 hours)
     * `'Afternoon'` (12-18 hours)
     * `'Evening'` (18-24 hours)
7. **Column Trimming**:
   * Drops unused internal noise columns: `is_cutoff`, `cutoff_factor`, and `cutoff_timestamp`.

---

## How to Run

Run this script using the virtual environment Python:

```bash
python cleaning/clean.py
```
