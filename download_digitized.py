import json
import requests
import time
import pymongo
from config.config import logger

mongo_server_host = 'mongodb://localhost:27017/?readPreference=primary&ssl=false'
mongo_wfm_db = 'bulk_script_db'
mongo_wfm_jobs_col = 'download_digitized'
max_retries = 10
mongo_instance = None

def instantiate():
    global mongo_instance
    client = pymongo.MongoClient(mongo_server_host)
    db = client[mongo_wfm_db]
    mongo_instance = db[mongo_wfm_jobs_col]
    return mongo_instance

def get_mongo_instance():
    global mongo_instance
    if mongo_instance is None:
        return instantiate()
    else:
        return mongo_instance

# Searches the object into mongo collection
def search_job(query, exclude = None, offset = None, res_limit = None):
    col = get_mongo_instance()
    if offset is None and res_limit is None:
        res = col.find(query)
    else:
        res = col.find(query, exclude).sort([('_id', -1)]).skip(offset).limit(res_limit)
    result = []
    for record in res:
        result.append(record)
    return result

def update_job(filename,object_in):
    col = get_mongo_instance()
    col.update_one(
        {"filename": filename},
        { "$set": object_in }
    )

i=0

files = search_job({})

total_files = len(files)

for each_job in files:
    if each_job["downloaded"] == True:
        break
    file_name = each_job["filename"]
    download_name = each_job["downloadname"]
    logger.debug(f"File {i} out of {total_files} named {download_name}")
    i=i+1
    logger.debug("Performing call")
    for retry_count in range(max_retries):
        try:
            url = f"https://jud-auth.anuvaad.org/download/{file_name}"
            response = requests.request("GET", url, timeout=15)
            response.raise_for_status()  # Check for HTTP errors
            with open("./temporary/digitized_files/"+download_name,"wb") as file:
                file.write(response.content)
            if response.status_code >=200 and response.status_code <=204:
                logger.debug("File Downloaded")
                update_job(file_name,{"downloaded":True})
            break  # Successful request, exit the loop
        except requests.exceptions.RequestException as e:
            logger.debug(f"Retry {retry_count + 1}/{max_retries}: {e}")
            time.sleep(15)

