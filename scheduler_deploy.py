import os
import shutil
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(filename='mongo_backup_deleted.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def delete_old_backup_folders(source_folder, retention_period_hours=48):
    # Get current date and time
    current_time = datetime.now()

    # Calculate the timestamp for retention
    retention_timestamp = current_time - timedelta(hours=retention_period_hours)

    # List all folders in the source folder with modification times
    all_folders = [(os.path.join(source_folder, folder), os.path.getmtime(os.path.join(source_folder, folder))) for folder in os.listdir(source_folder)]

    # Initialize a list to store folder names older than retention period
    folders_to_delete = []

    # Find folders older than retention period
    for folder_path, modified_time in all_folders:
        # Check if it's a directory
        if os.path.isdir(folder_path):
            # Check if the folder is older than the retention period
            if datetime.fromtimestamp(modified_time) < retention_timestamp:
                folders_to_delete.append(folder_path)

    # Check if current day's folder exists and at least 2 additional folders exist
    current_day_folder_exists = any(datetime.fromtimestamp(modified_time).date() == current_time.date() for _, modified_time in all_folders)
    additional_folders_exist = len(all_folders) > 3

    # Delete old backup folders if conditions are met
    if current_day_folder_exists and additional_folders_exist:
        for folder in folders_to_delete:
            shutil.rmtree(folder)
            log_message = f"Deleted folder: {folder}"
            logging.info(log_message)
            print(log_message)
    else:
        log_message = "No folders deleted. Conditions not met."
        logging.info(log_message)
        print(log_message)

# Example usage
source_folder = "/home/aswin/Downloads/mongo_backup_trial_march2"

while True:
    # Run the deletion function
    delete_old_backup_folders(source_folder, retention_period_hours=48)
    # Sleep for 1 hour
    time.sleep(3600)  # 3600 seconds = 1 hour
