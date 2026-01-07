"""
Generic dataset preprocessing script for federated learning.
Performs one-hot encoding before splitting data across federated learning sites.

This approach:
1. Ensures all sites have identical feature sets
2. Creates multiple CSV files ready for upload to different sites. (For now, two files but script can be modified for more)

Usage:
    python preprocess_dataset.py <input_csv> <output_site1_csv> <output_site2_csv>
"""

import sys
import pandas as pd
import numpy as np


def preprocess_and_split(input_file, output_site1, output_site2):
    """
    Preprocess any CSV dataset and split it into two sites for federated learning.
    
    Steps:
    1. Load the CSV
    2. Convert numeric columns from strings to proper numeric types
    3. One-hot encode categorical columns
    4. Split the data (50-50 split)
    5. Save two separate CSV files for Site 1 and Site 2
    """
    print(f"Loading data from {input_file}...")
    # Read CSV
    df = pd.read_csv(input_file)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Column names: {list(df.columns)}")
    
    # Step 1: Convert string numbers to actual numeric types
    print("\nConverting numeric columns...")
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    
    # Step 2: Identify categorical vs numeric columns
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    print(f"\nCategorical columns ({len(categorical_cols)}): {categorical_cols}")
    print(f"Numeric columns ({len(numeric_cols)}): {numeric_cols}")
    
    # Step 2.5: Drop 'Country' column to avoid feature explosion (too many unique values)
    # Keep only 'Region' which has fewer categories (~9 vs ~193)
    if 'Country' in categorical_cols:
        categorical_cols.remove('Country')
        df = df.drop('Country', axis=1)
        print(f"\nDropped 'Country' column (too many unique values)")
        print(f"Remaining categorical columns: {categorical_cols}")
    
    # Step 3: One-hot encode categorical columns
    if categorical_cols:
        print(f"\nOne-hot encoding {len(categorical_cols)} categorical columns...")
        df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=False)
        
        # Convert boolean columns to integers (0 and 1) for compatibility
        bool_cols = df_encoded.select_dtypes(include=['bool']).columns
        if len(bool_cols) > 0:
            print(f"Converting {len(bool_cols)} boolean columns to integers...")
            df_encoded[bool_cols] = df_encoded[bool_cols].astype(int)
        
        # Move target variable (Life_expectancy) to the last column
        # This ensures read_dataset correctly splits X (all columns except last) and y (last column)
        if 'Life_expectancy' in df_encoded.columns:
            life_exp_col = df_encoded.pop('Life_expectancy')
            df_encoded['Life_expectancy'] = life_exp_col
            print(f"Moved 'Life_expectancy' to last column for proper train/test split")
        
        print(f"After encoding shape: {df_encoded.shape}")
        print(f"New columns: {df_encoded.shape[1] - len(numeric_cols)} one-hot features created")
    else:
        df_encoded = df
        print("\nNo categorical columns to encode")
    
    # Step 4: Split the data
    # Shuffle for random distribution
    df_shuffled = df_encoded.sample(frac=1, random_state=42).reset_index(drop=True)
    
    split_point = len(df_shuffled) // 2
    site1_data = df_shuffled.iloc[:split_point]
    site2_data = df_shuffled.iloc[split_point:]
    
    print(f"\nSplitting data:")
    print(f"  Site 1: {len(site1_data)} rows")
    print(f"  Site 2: {len(site2_data)} rows")
    
    # Step 5: Save the files without headers (Starfish reads with header=None)
    site1_data.to_csv(output_site1, index=False, header=False)
    site2_data.to_csv(output_site2, index=False, header=False)
    
    print(f"\nSuccessfully created:")
    print(f"   {output_site1}")
    print(f"   {output_site2}")
    print(f"\nBoth files have {df_encoded.shape[1]} columns (including one-hot encoded features)")
    print(f"\nYou can now upload these files as datasets for Site 1 and Site 2")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python preprocess_dataset.py <input_csv> <output_site1_csv> <output_site2_csv>")
        print("\nExample:")
        print("  python preprocess_dataset.py dataset.csv site1_data.csv site2_data.csv")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_site1_csv = sys.argv[2]
    output_site2_csv = sys.argv[3]
    
    preprocess_and_split(input_csv, output_site1_csv, output_site2_csv)
