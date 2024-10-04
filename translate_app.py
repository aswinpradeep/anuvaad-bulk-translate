# Login - UserID & auth-token


# max_uploads = 5
# cur_uploads = 0
# current_jobs_digitized = {}

# input = Get List of Files in input folder

# while len(input)>0: 
#     while cur_uploads <= max_uploads:
#         Upload-file, initiate [digitization]
#         if success:
#             cur_uploads += 1
#             current_jobs_digitized[input_file] = job_id
#     call bulk
#     if any current_jobs_digitized are completed in bulk:  
#         cur_uploads -= 1
#         download the target file 
#         move the input and target file to a folder 
#         remove current_jobs_digitized[input_file]
#     time.sleep()

from config.config import *
import requests
from service.api_calls import APICalls
import os
import time
import threading
from config.config import logger

MAX_UPLOADS = 5
#current_uploads = 0
current_jobs_translated = {}

apicalls = APICalls()

token = apicalls.login()
user_id = apicalls.auth_token_search(token)    

#For search and download queue
input_files = os.listdir(os.getcwd()+INPUT_DIRECTORY)
#For upload and translate queue
input_files_translated = input_files.copy()
logger.debug(input_files)

while(len(input_files)>0):
    while len(current_jobs_translated) < MAX_UPLOADS and len(input_files_translated) > 0:
            file_id = apicalls.upload_files(os.getcwd()+INPUT_DIRECTORY+input_files_translated[0],token)
            jobID, startTime = apicalls.translate(input_files_translated[0],file_id,token)
            if jobID:
                current_jobs_translated[jobID] = {"startTime":startTime,
                                    "filename":input_files_translated[0],
                                    "fileid":file_id}
                input_files_translated.pop(0)
    time.sleep(BULK_WAIT_TIME)
    status_data = apicalls.get_status_of_jobs(list(current_jobs_translated.keys()),token)
    logger.debug(status_data)
    for job in status_data:
        if(job["status"] == "COMPLETED"):
            logger.debug(f"JOB ID: {job['jobID']} and status: {job['status']}")
            record_id = str(job["jobID"])+"|"+str(job["output"])
            file_content = apicalls.download_translated_file(
                 current_jobs_translated[job['jobID']]["fileid"], 
                 user_id, token)
            translated_file = "input/"+current_jobs_translated[job['jobID']]["filename"]+"_translated.pdf"
            #Download Translated File
            with open(translated_file, "wb") as file:
                file.write(file_content)
                try:
                    #current_jobs_translated.remove(current_jobs_translated[job['jobID']]["filename"])
                    current_jobs_translated.pop(job['jobID'])
                    input_files.remove(translated_file)
                except: 
                    logger.debug("Filename not found")


