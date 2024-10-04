import threading
import time
from config.config import *
import os
import traceback
# from utils.utils import Utilities
from service.api_calls import APICalls
from service.docx_generator import Docx_Generator
from repo.repo import WFMRepository
import time
import datetime
import sys
import dateutil.relativedelta
from config.config import logger
import traceback

# utils = Utilities()
apicalls = APICalls()
docx_gen = Docx_Generator()
wfmrepo = WFMRepository()

# Function to add elements to the queue
def digitize():
    global token
    global user_id
    #Read all files from input folder
    input_files = os.listdir(os.getcwd()+INPUT_DIRECTORY)
    #Remove digitized files from input_files
    input_files_digitized = [i for i in input_files if 'digitized' in i]
    input_files = [i for i in input_files if 'digitized' not in i]
    for i in input_files_digitized:
        if i.replace("_digitized","") in input_files:
            input_files.remove(i.replace("_digitized",""))
    input_files.sort()
    logger.debug(input_files)
    current_jobs_digitized = {}
    while True:
        #Digitization Script
        try:
            while len(current_jobs_digitized) < MAX_DIGITIZATION_UPLOADS and len(input_files)>0:
                if len(input_files)>0:
                    result = wfmrepo.search_job({"filename":input_files[0]})
                    #If the file is already uploaded
                    if len(result) > 0:
                        input_files.pop(0)
                        continue
                    #Upload the file
                    logger.debug(f"Uploading file for digitization : {input_files[0]}")
                    file_id = apicalls.upload_files(os.getcwd()+INPUT_DIRECTORY+input_files[0],token)
                    if file_id is None:
                        continue
                    jobID, startTime = apicalls.digitize(input_files[0],file_id,token)
                    if jobID is None:
                        continue
                    digitized_data = {
                        "filename" : input_files[0],
                        "digitization" : {
                            "jobID" : jobID,
                            "startTime":startTime
                        },
                        "current_status" : "digitizationProgress"
                    }
                    #Add to database
                    wfmrepo.create_job(digitized_data)
                    current_jobs_digitized[jobID] = {"startTime":startTime,
                                                "filename":input_files[0]}
                    input_files.pop(0)
                
                if len(current_jobs_digitized) == 0:
                    continue

            #Perform bulk search for files being digitized
            status_data = {}
            time.sleep(30)
            if len(current_jobs_digitized)!=0:
                status_data = apicalls.get_status_of_jobs(list(current_jobs_digitized.keys()),token)
            #logger.debug(f"STATUS DATA :: {status_data}")
            for job in status_data:
                if(job["status"] == "COMPLETED"):
                    logger.debug(f"JOB ID: {job['jobID']} and status: {job['status']}")
                    record_id = str(job["jobID"])+"|"+str(job["output"])
                    #Download digitized file
                    document = apicalls.document_export(user_id, record_id, token)
                    file_content = apicalls.download_file(document, token)
                    digitized_file = "input/"+current_jobs_digitized[job['jobID']]["filename"].replace(".pdf","")+"_digitized.pdf"
                    with open(digitized_file, "wb") as file:
                        file.write(file_content)
                    digitized_copy = "digitized/"+current_jobs_digitized[job['jobID']]["filename"].replace(".pdf","")+"_digitized.pdf"
                    with open(digitized_copy, "wb") as file:
                        file.write(file_content)
                    wfmrepo.update_job(current_jobs_digitized[job['jobID']]["filename"],{"current_status" : "digitizationCompleted"})
                    current_jobs_digitized.pop(job['jobID'])
        except Exception as e:
            logger.debug(f"Exception {e} has occurred")
    
# Function to receive from the queue and perform operations
def translate():



    global token
    global user_id
    #Read all files from input folder
    input_files = os.listdir(os.getcwd()+INPUT_DIRECTORY)
    #Remove digitized files from input_files
    input_files_digitized = [i for i in input_files if 'digitized' in i]
    input_files_digitized.sort()
    logger.debug(input_files_digitized)


    global token
    global user_id
    current_jobs_translated = {}
    while True:
        try:
            time.sleep(5)


            while len(current_jobs_translated) < MAX_TRANSLATION_UPLOADS and len(input_files_digitized)>0:
                if len(input_files_digitized)>0:
                    result = wfmrepo.search_job({"filename":input_files_digitized[0]})
                    #If the file is already uploaded
                    if len(result) > 0:
                        input_files_digitized.pop(0)
                        continue
                    #Upload the file
                    logger.debug(f"Uploading file for digitization : {input_files_digitized[0]}")
                    filename = input_files_digitized[0]
                    file_id = apicalls.upload_files(os.getcwd()+INPUT_DIRECTORY+input_files_digitized[0],token)
                    if file_id is None:
                        continue
                    jobID, startTime = apicalls.translate(input_files_digitized[0],file_id,token)
                    if jobID is None: 
                        continue
                    db_entry = {}
                    db_entry["translation"] = {
                        "jobID":jobID,
                        "startTime":startTime
                    }
                    wfmrepo.update_job(filename, db_entry)
                    current_jobs_translated[jobID] = {"startTime":startTime,
                                        "filename":filename,
                                        "fileid":file_id}
                    wfmrepo.update_job(filename, {"current_status":"translationProgress"})
                    # result.pop(0)
                    input_files_digitized.pop(0)

            #perform bulk search
            if len(current_jobs_translated) == 0:
                continue
            time.sleep(30)
            status_data = apicalls.get_status_of_jobs(list(current_jobs_translated.keys()),token)
            logger.debug(status_data)
            for job in status_data:
                if(job["status"] == "FAILED"):
                    logger.debug(f"TRANSLATION FAILED FOR THE JOB :: {job['jobID']} {current_jobs_translated[job['jobID']]['filename']}")
                    # wfmrepo.delete_job({"translation.jobID":job['jobID']})
                    current_jobs_translated.pop(job['jobID'])
                if(job["status"] == "COMPLETED"):
                    logger.debug(f"JOB ID: {job['jobID']} and status: {job['status']}")
                    fname = str(job["output"].split('.')[0])+".docx"
                    record_id = str(job["output"].split('.')[0])+".json"
                    record_id = record_id.replace('|','%7C')
                    fetch_content_response = apicalls.fetch_content(record_id,token)
                    upload_file_name = current_jobs_translated[job['jobID']]["filename"]+".docx"
                    upload_file_name = upload_file_name.replace("_digitized.pdf","")
                    upload_file_name = upload_file_name.replace(".pdf","")
                    search_file_name = upload_file_name.split(".docx")[0]
                    translated_file = "./output/"+upload_file_name
                    docx_gen.generate_docx(fetch_content_response,translated_file)
                    files = os.listdir(os.getcwd()+INPUT_DIRECTORY)
                    # Iterate through the files and delete those containing the target string
                    for file_name in files:
                        if search_file_name in file_name:
                            file_path = os.path.join("."+INPUT_DIRECTORY, file_name)
                            os.remove(file_path)
                            logger.debug(f"Deleted: {file_path}")
                    # wfmrepo.update_job(current_jobs_translated[job['jobID']]["filename"],{"current_status" : "translationCompleted"})
                    current_jobs_translated.pop(job['jobID'])

        except Exception as e:
            logger.debug(f"Exception {e} has occurred")
            logger.debug(f"Traceback {traceback.format_exc()}")



def cron():
    #Check for digitization in progress since 1 hours and see if it should be downloaded
    global token
    while True:
        try:
            time.sleep(60*120)
            #Perform bulk search, download file and mark digitization to be completed
            result = wfmrepo.search_job({"current_status": "translationProgress"})
            if len(result) == 0:
                continue
            current_time = round(time.time())
            for each_result in result:
                logger.debug(f"Job Details :: {each_result}")
                logger.debug(f"Cron running for job ID {each_result['translation']['jobID']}")
                translation_time = int(str(each_result["translation"]["startTime"])[:-3])
                current_time = round(time.time())
                dt1 = datetime.datetime.fromtimestamp(translation_time) # 1973-11-29 22:33:09
                dt2 = datetime.datetime.fromtimestamp(current_time) # 1977-06-07 23:44:50
                rd = dateutil.relativedelta.relativedelta (dt2, dt1)
                if rd.days>=1 or rd.hours>=2:
                    logger.debug(f'Job ID : {[each_result["translation"]["jobID"]]}')
                    status_data = apicalls.get_status_of_jobs([each_result["translation"]["jobID"]],token)
                    logger.debug(status_data)
                    for job in status_data:
                        if(job["status"] == "COMPLETED"):
                            logger.debug(f"JOB ID: {job['jobID']} and status: {job['status']}")
                            fname = str(job["output"].split('.')[0])+".docx"
                            record_id = str(job["output"].split('.')[0])+".json"
                            record_id = record_id.replace('|','%7C')
                            fetch_content_response = apicalls.fetch_content(record_id,token)
                            upload_file_name = each_result["filename"]+".docx"
                            upload_file_name = upload_file_name.replace("_digitized.pdf","")
                            upload_file_name = upload_file_name.replace(".pdf","")
                            search_file_name = upload_file_name.split(".docx")[0]
                            translated_file = "./output/"+upload_file_name
                            docx_gen.generate_docx(fetch_content_response,translated_file)
                            files = os.listdir(os.getcwd()+INPUT_DIRECTORY)
                            # Iterate through the files and delete those containing the target string
                            for file_name in files:
                                if search_file_name in file_name:
                                    file_path = os.path.join("."+INPUT_DIRECTORY, file_name)
                                    os.remove(file_path)
                                    logger.debug(f"Deleted: {file_path}")
                            wfmrepo.update_job(each_result["filename"],{"current_status" : "translationCompleted"})


        except Exception as e:
            logger.debug(f"Exception {e} has occurred")

if __name__ == "__main__":
    token = apicalls.login()
    user_id = apicalls.auth_token_search(token)    

    # Create two threads
    # digitize_thread = threading.Thread(target=digitize)
    translate_thread = threading.Thread(target=translate)
    # cron_thread = threading.Thread(target=cron)

    # Start the threads
    # digitize_thread.start()
    translate_thread.start()
    # cron_thread.start()

    # Wait for both threads to finish
    # digitize_thread.join()
    translate_thread.join()
    # cron_thread.join()
    python = sys.executable
    os.execl(python, python, *sys.argv)