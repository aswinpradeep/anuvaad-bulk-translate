from config.config import *
from utils.utils import Utilities
import requests
from service.api_calls import APICalls
from service.docx_generator import Docx_Generator
import os
import time
import threading
import pandas as pd
import re
from urllib.parse import urlparse, parse_qs
import json
import sys
import traceback
from config.config import logger

global_variable_lock = threading.Lock()
#current_uploads = 0
current_jobs_digitized = {}
current_jobs_translated = {}

utils = Utilities()
apicalls = APICalls()
docx_gen = Docx_Generator()

if INPUT_TYPE == "EXCEL":
    utils.download_files()

token = None
user_id = None   

input_files = []
input_files_2 = []
input_files_digitized = []
input_files_translated = []

# input_files_copy = []

# for file in input_files:
#     if "_digitized" in file:
#         original = file.replace("_digitized","")
#         input_files_2.append(file)
#         input_files_translated.append(file)
#     else:
#         digitized_file = file.replace(".pdf","_digitized.pdf")
#         if not digitized_file in input_files:
#             input_files_copy.append(file)

# input_files = input_files_copy
# input_files_digitized = input_files_copy

def restart_program():
    logger.debug("Restarting the program...")
    # Implement any cleanup or resource release logic here if needed
    time.sleep(1)  # Wait for a moment before restarting

    # Create thread objects for producer and consumer functions
    digitization_thread = threading.Thread(target=digitization)
    translation_thread = threading.Thread(target=translation)
    
    # Start both threads
    digitization_thread.start()
    translation_thread.start()
    
    try:
        # Keep the main thread running
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        # Terminate threads when user interrupts with Ctrl+C
        digitization_thread.join()
        translation_thread.join()

# https://becominghuman.ai/how-to-automatically-deskew-straighten-a-text-image-using-opencv-a0c30aed83df

    #python = sys.executable
    #os.execl(python, python, *sys.argv)

def digitization():
    global token
    global input_files
    global input_files_digitized
    global input_files_translated
    global input_files_2
    while len(input_files_digitized)>0:
        #Digitization Script
        try:
            while len(current_jobs_digitized) < MAX_UPLOADS and len(input_files) > 0:
                file_id = apicalls.upload_files(os.getcwd()+INPUT_DIRECTORY+input_files[0],token)
                if file_id:
                    jobID, startTime = apicalls.digitize(input_files[0],file_id,token)
                    if jobID:
                        current_jobs_digitized[jobID] = {"startTime":startTime,
                                            "filename":input_files[0]}
                        input_files.pop(0)
            time.sleep(BULK_WAIT_TIME)
            status_data = apicalls.get_status_of_jobs(list(current_jobs_digitized.keys()),token)
            logger.debug(status_data)
            for job in status_data:
                if(job["status"] == "COMPLETED"):
                    logger.debug(f"JOB ID: {job['jobID']} and status: {job['status']}")
                    record_id = str(job["jobID"])+"|"+str(job["output"])
                    document = apicalls.document_export(user_id, record_id, token)
                    file_content = apicalls.download_file(document, token)
                    digitized_file = "input/"+current_jobs_digitized[job['jobID']]["filename"].replace(".pdf","")+"_digitized.pdf"
                    #Download digitized file and add it to translation list
                    # digitized_file_copy = "data_input/digitized/"+current_jobs_digitized[job['jobID']]["filename"].replace(".pdf","")+"_digitized.pdf"
                    # with open(digitized_file_copy, "wb") as file:
                    #     file.write(file_content)
                    with open(digitized_file, "wb") as file:
                        file.write(file_content)
                        # file_lock.acquire()
                        # df = pd.read_excel("./data_input/SC.xlsx")
                        # # Create a new DataFrame with the data to append
                        # new_data = pd.DataFrame({'Filename': [current_jobs_digitized[job['jobID']]["filename"]],
                        #                         'Digitization Record ID': [record_id],
                        #                         'Translation Record ID': ['']})

                        # # Concatenate the DataFrames
                        # df = pd.concat([df, new_data], ignore_index=True)
                        # df.to_excel("./data_input/SC.xlsx",index=False)
                        # file_lock.release()
                        try:
                            with global_variable_lock:
                                input_files_digitized.remove(current_jobs_digitized[job['jobID']]["filename"])
                                input_files_2.append(current_jobs_digitized[job['jobID']]["filename"].replace(".pdf","")+"_digitized.pdf")
                                input_files_translated.append(current_jobs_digitized[job['jobID']]["filename"].replace(".pdf","")+"_digitized.pdf")
                                current_jobs_digitized.pop(job['jobID'])
                        except Exception as e: 
                            logger.debug(f"Filename not found with exception {e}")
        except Exception as e:
            logger.debug(f"Exception {e} has occurred")
            traceback.logger.debug_exc()            
            restart_program()

def translation():
    global token
    global input_files_translated
    global input_files_2
    while 1:
        try:
            while(len(input_files_2)>0):
                while len(current_jobs_translated) < MAX_UPLOADS and len(input_files_translated) > 0:
                        with global_variable_lock:
                            file_id = apicalls.upload_files(os.getcwd()+INPUT_DIRECTORY+input_files_translated[0],token)
                        jobID, startTime = apicalls.translate(input_files_translated[0],file_id,token)
                        if jobID:
                            current_jobs_translated[jobID] = {"startTime":startTime,
                                                "filename":input_files_translated[0],
                                                "fileid":file_id}
                            with global_variable_lock:
                                input_files_translated.pop(0)
                time.sleep(BULK_WAIT_TIME)
                status_data = apicalls.get_status_of_jobs(list(current_jobs_translated.keys()),token)
                logger.debug(status_data)
                for job in status_data:
                    if(job["status"] == "COMPLETED"):
                        logger.debug(f"JOB ID: {job['jobID']} and status: {job['status']}")
                        fname = str(job["output"].split('.')[0])+".docx"
                        record_id = str(job["output"].split('.')[0])+".json"
                        record_id = record_id.replace('|','%7C')
                        # TO DOWNLOAD DOCX GENERATED:
                        # file_content = apicalls.download_translated_docx_file(
                        #     fname, record_id, current_jobs_translated[job['jobID']]["filename"], token)
                        # if INPUT_TYPE == "EXCEL":
                        #     upload_file_name = "2023_SC_"+current_jobs_translated[job['jobID']]["filename"]+"_en_hi.docx"
                        # else:
                        #     upload_file_name = current_jobs_translated[job['jobID']]["filename"]+".docx"                                        
                        # upload_file_name = upload_file_name.replace("_digitized.pdf","")
                        # search_file_name = upload_file_name.split(".docx")[0]
                        # translated_file = "output/"+upload_file_name
                        # #Download Translated File
                        # with open(translated_file, "wb") as file:
                        #     file.write(file_content)
                        fetch_content_response = apicalls.fetch_content(record_id,token)
                        upload_file_name = current_jobs_translated[job['jobID']]["filename"]+".docx"
                        upload_file_name = upload_file_name.replace("_digitized.pdf","")
                        search_file_name = upload_file_name.split(".docx")[0]
                        translated_file = "./output/"+upload_file_name
                        #fetch_content_json = json.load(fetch_content_response)
                        # with open("./output/"+search_file_name+"_fetch_content.json", "wb") as file:
                        #     # Convert the string to bytes using UTF-8 encoding
                        #     content_bytes = fetch_content_response.encode('utf-8')
                        #     # Write the bytes to the file
                        #     file.write(content_bytes)
                        docx_gen.generate_docx(fetch_content_response,translated_file)
                        # file_lock.acquire()
                        # df = pd.read_excel("./data_input/SC.xlsx")
                        # if df['Filename'].eq(current_jobs_translated[job['jobID']]["filename"]).any():
                        #     df.loc[df["Filename"] == current_jobs_translated[job['jobID']]["filename"],"Translation Record ID"] = record_id
                        #     df.to_excel("./data_input/SC.xlsx",index=False)
                        # file_lock.release()
                        if INPUT_TYPE == "EXCEL":
                                utils.upload_s3_client("./"+translated_file,upload_file_name,current_jobs_translated[job['jobID']]["filename"])
                        try:
                            # List all files in the folder
                            with global_variable_lock:
                                input_files_2.remove(current_jobs_translated[job['jobID']]["filename"])
                            current_jobs_translated.pop(job['jobID'])
                            files = os.listdir(os.getcwd()+INPUT_DIRECTORY)
                            # Iterate through the files and delete those containing the target string
                            for file_name in files:
                                if search_file_name in file_name:
                                    file_path = os.path.join("."+INPUT_DIRECTORY, file_name)
                                    os.remove(file_path)
                                    logger.debug(f"Deleted: {file_path}")
                        except Exception as e: 
                            logger.debug("Filename not found with exception {e}")
        except Exception as e:
            logger.debug(f"Exception {e} has occurred")
            traceback.logger.debug_exc()            
            restart_program()

if __name__ == "__main__":

    input_files = os.listdir(os.getcwd()+INPUT_DIRECTORY)

    input_files_set = set(input_files)
    input_files_2_set = set()

    for i in input_files_set:
        if "digitized" in i:
            input_files_2_set.add(i)

    for i in input_files_2_set:
        input_files_set.discard(i.replace("_digitized",""))

    input_files_set = input_files_set - input_files_2_set

    input_files = list(input_files_set)

    input_files.sort()
    input_files_digitized = input_files.copy()
    input_files_2 = list(input_files_2_set)
    input_files_translated = list(input_files_2_set)


    logger.debug(input_files)
    logger.debug(input_files_translated)
    token = apicalls.login()
    user_id = apicalls.auth_token_search(token)    

    # Create thread objects for producer and consumer functions
    digitization_thread = threading.Thread(target=digitization)
    translation_thread = threading.Thread(target=translation)
    
    # Start both threads
    digitization_thread.start()
    translation_thread.start()
    
    try:
        # Keep the main thread running
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        # Terminate threads when user interrupts with Ctrl+C
        digitization_thread.join()
        translation_thread.join()

# https://becominghuman.ai/how-to-automatically-deskew-straighten-a-text-image-using-opencv-a0c30aed83df
