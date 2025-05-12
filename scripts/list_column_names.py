import os
import pandas as pd

import os
import pandas as pd

import os
import pandas as pd

import os
import pandas as pd


def create_sample_parquet(source_file: str, output_file: str):
    try:
        df = pd.read_parquet(source_file)
        sample_df = df.head(1)

        base, ext = os.path.splitext(output_file)
        latest_version = 0
        latest_file = output_file

        # Find the latest version of the file
        while os.path.exists(f"{base}_v{latest_version}{ext}"):
            latest_file = f"{base}_v{latest_version}{ext}"
            latest_version += 1

        if os.path.exists(latest_file):
            existing_df = pd.read_parquet(latest_file)
            if list(existing_df.columns) == list(sample_df.columns):
                print(f"File already exists with the same columns: {latest_file}")
                return
            else:
                output_file = f"{base}_v{latest_version}{ext}"

        # Save the sample Parquet file
        sample_df.to_parquet(output_file, index=False)
        print(f"Sample Parquet file created: {output_file}")

        # Save the sample as a CSV file
        csv_file = f"{base}_v{latest_version}.csv"
        sample_df.to_csv(csv_file, index=False)
        print(f"Sample CSV file created: {csv_file}")

        # Create a .txt file with column names
        columns_file = f"{base}_v{latest_version}_columns.txt"
        with open(columns_file, "w", encoding="utf-8") as f:
            f.write("\n".join(sample_df.columns))
        print(f"Columns file created: {columns_file}")

    except Exception as e:
        print(f"Error processing file {source_file}: {e}")


def find_first_prquet_file(directory):
    """
    Recursively searches for the first .parquet file in the given directory and its subdirectories.

    Args:
        directory (str): The directory to search.

    Returns:
        str or None: The path to the first .parquet file found, or None if no file is found.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.parquet'):
                return os.path.join(root, file)
    return None


def process_directories(base_dir: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    for category in ['features', 'filtered']:
        category_path = os.path.join(base_dir, category)
        if not os.path.exists(category_path):
            print(f"Directory not found: {category_path}")
            continue

        for sub_dir in ['day', 'minute', 'trades']:
            sub_dir_path = os.path.join(category_path, "us", "stocks", sub_dir)
            print(f"Searching in directory: {sub_dir_path}")
            source_file = find_first_prquet_file(sub_dir_path)
            if source_file:
                print(f"Found file: {source_file}")
                output_file = os.path.join(
                    output_dir,
                    f"{category}_{sub_dir}_sample.parquet"
                )
                create_sample_parquet(source_file, output_file)
            else:
                print(f"No .parquet file found in: {sub_dir_path}")


# Example usage
if __name__ == "__main__":
    base_directory = "D:\\tradebotnanData"
    output_directory = "D:\\tradebotnanData\\sample_files"
    process_directories(base_directory, output_directory)
