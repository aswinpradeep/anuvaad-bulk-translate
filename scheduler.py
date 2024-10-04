import os
from datetime import datetime, timedelta
import shutil
import time

LOG_FILE = "delete_log.txt"

def remove_old_folders(folder_path, threshold_hours=1):
    current_time = datetime.now()

    with open(LOG_FILE, "a") as log:
        log.write(f"--- {current_time} ---\n")

        for folder_name in os.listdir(folder_path):
            folder_path_full = os.path.join(folder_path, folder_name)

            # Get the folder creation time
            creation_time = datetime.fromtimestamp(os.path.getctime(folder_path_full))

            # Calculate the age of the folder in hours
            age_in_hours = (current_time - creation_time).total_seconds() / 3600

            # Check if the folder is older than the threshold
            if age_in_hours < threshold_hours:
                log.write(f"Skipping {folder_name}, not older than {threshold_hours} hours.\n")
            else:
                try:
                    # Remove the folder and its contents, and log the deletion
                    shutil.rmtree(folder_path_full)
                    log.write(f"Removed {folder_name}, {age_in_hours} hours old.\n")
                except Exception as e:
                    log.write(f"Error removing {folder_name}: {e}\n")

if __name__ == "__main__":
    backup_folder = "/home/aswin/Downloads/mongo_backup_trial_march"

    while True:
        remove_old_folders(backup_folder)
        # Sleep for a specific interval before checking again (e.g., every hour)
        time.sleep(3600)