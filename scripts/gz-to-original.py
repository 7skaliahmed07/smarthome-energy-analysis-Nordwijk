
import gzip
import shutil
import os
from pathlib import Path


def convert_gz_to_original(source_folder, target_folder):
    Path(target_folder).mkdir(parents=True, exist_ok=True)
    gz_files = Path(source_folder).glob('*.gz')
    print(f"==>> gz_files: {gz_files}")

    for gz_file in gz_files:
        # Automatically removes .gz extension
        csv_file = Path(target_folder) / gz_file.stem
        with gzip.open(gz_file, 'rb') as f_in:
            with open(csv_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"Converted: {gz_file.name} -----> {csv_file.name}")


# Base directory
base_dir = r"D:\Leiden\EFDS\smarthome-energy-analysis-Nordwijk\data"

# Folders to process
folders = ['P1e', 'P1g', 'smartthings']

for folder in folders:
    source_folder = os.path.join(base_dir, folder)
    target_folder = os.path.join(base_dir, folder, "gz-to-csv")

    print(f"\nProcessing folder: {folder}")
    convert_gz_to_original(source_folder, target_folder)

print("\n Boom ... All files in all folders converted successfully from GZ to CSV/TSV..!")
