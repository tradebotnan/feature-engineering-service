from pathlib import Path

import pandas as pd


def compare_parquet_files_exact(file1_path: Path, file2_path: Path) -> bool:
    print(f"🔍 Comparing:\n  1️⃣ {file1_path}\n  2️⃣ {file2_path}")

    try:
        df1 = pd.read_parquet(file1_path)
        df2 = pd.read_parquet(file2_path)
    except Exception as e:
        print(f"❌ Failed to read Parquet files: {e}")
        return False

    # Basic shape check
    if df1.shape != df2.shape:
        print(f"❌ Shape mismatch: {df1.shape} vs {df2.shape}")
        return False

    # Check columns
    if list(df1.columns) != list(df2.columns):
        print("❌ Column mismatch:")
        print("  File 1 Columns:", df1.columns.tolist())
        print("  File 2 Columns:", df2.columns.tolist())
        return False

    # Compare row-by-row, column-by-column
    for idx in range(len(df1)):
        for col in df1.columns:
            val1 = df1.iloc[idx][col]
            val2 = df2.iloc[idx][col]

            if pd.isna(val1) and pd.isna(val2):
                continue

            if not pd.isna(val1) and not pd.isna(val2):
                if val1 != val2:
                    print(f"❌ Mismatch at row {idx}, column '{col}':")
                    print(f"  File 1 → {val1}")
                    print(f"  File 2 → {val2}")
                    return False
            else:
                print(f"❌ Mismatch at row {idx}, column '{col}':")
                print(f"  One is NaN, the other is not → File 1: {val1}, File 2: {val2}")
                return False

    print("✅ Files are exactly identical")
    return True


def convert_parquet_to_csv(parquet_file: str, csv_file: str) -> None:
    """
    Converts a Parquet file to a CSV file.

    Args:
        parquet_file (str): Path to the input Parquet file.
        csv_file (str): Path to the output CSV file.
    """
    try:
        # Read the Parquet file
        df = pd.read_parquet(parquet_file)

        # Write to CSV
        df.to_csv(csv_file, index=False)
        print(f"✅ Successfully converted {parquet_file} to {csv_file}")
    except Exception as e:
        print(f"❌ Error converting {parquet_file} to CSV: {e}")


def check_parquet_files_match(file1_path: str, file2_path: str) -> None:
    """
    Compares two Parquet files and prints whether they match.
    """
    file1 = Path(file1_path)
    file2 = Path(file2_path)
    match = compare_parquet_files_exact(file1, file2)
    print("✅ Match!" if match else "❌ Mismatch!")


def convert_parquet_to_csv_file(parquet_file_path: str, csv_file_path: str) -> None:
    """
    Converts a Parquet file to a CSV file.
    """
    convert_parquet_to_csv(parquet_file_path, csv_file_path)


if __name__ == "__main__":
    # check_parquet_files_match(
    #     r"D:\tradebotnanData\sample_files\base_filtered_us_stocks_day_AAPL_2015.parquet",
    #     r"D:\tradebotnanData\filtered\us\stocks\day\AAPL\2015\us_stocks_day_AAPL_2015.parquet"
    # )

    convert_parquet_to_csv_file(
        r"D:\tradebotnanData\features\us\stocks\minute\TSLA\2016-01\features_us_stocks_minute_TSLA_2016-01.parquet",
        r"D:\tradebotnanData\features\us\stocks\minute\TSLA\2016-01\features_us_stocks_minute_TSLA_2016-01.csv"
    )
