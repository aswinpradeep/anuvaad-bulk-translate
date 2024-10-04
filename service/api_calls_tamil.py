import json
from config.config import *
from config.credentials import *
import requests
import uuid
import time
max_retries = 5
retry_delay = 15  # seconds
from config.config import logger

class APICalls:
    def login(self):
        logger.debug("Performing Login")
        #hit login api and fetch auth-token
        login_body = {
            "userName":ANUVAAD_USERNAME,
            "password":ANUVAAD_PASSWORD,
        }

        for retry_count in range(max_retries):
            try:
                time.sleep(SLEEP_TIME)
                headers = {
                            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'
                }
                req = requests.post(timeout=120,url=ANUVAAD_LOGIN_URL,json=login_body, headers=headers)
                logger.debug(req.json())
                req.raise_for_status()  # Check for HTTP errors
                break  # Successful request, exit the loop
            except requests.exceptions.RequestException as e:
                logger.debug(f"Retry {retry_count + 1}/{max_retries}: {e}")
                time.sleep(retry_delay)
        if req.status_code >=200 and req.status_code <=204:
            token = req.json()["data"]["token"]
            return token
        else:
            return None

    def auth_token_search(self,token):
        #hit auth-token-search api and fetch userId
        logger.debug("Performing Auth Token Search")
        authsearch_body = {
            "token":token,
        }

        for retry_count in range(max_retries):
            try:
                time.sleep(SLEEP_TIME)
                headers = {
                            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'
                }
                req = requests.post(headers=headers,timeout=120,url=ANUVAAD_AUTHSEARCH_URL,json=authsearch_body)
                req.raise_for_status()  # Check for HTTP errors
                break  # Successful request, exit the loop
            except requests.exceptions.RequestException as e:
                logger.debug(f"Retry {retry_count + 1}/{max_retries}: {e}")
                time.sleep(retry_delay)

        if req.status_code >=200 and req.status_code <=204:
            user_id = req.json()["data"]["userID"]
            return user_id
        else:
            return None

    def upload_files(self,filepath,token):
        # hit upload_file api and fetch file_id
        logger.debug("Performing Upload File")

        for retry_count in range(max_retries):
            try:
                time.sleep(SLEEP_TIME)
                uploadfiles_body = {
                    'file': open(filepath,'rb')
                }
                logger.debug(f"File Uploaded :: {filepath}")
                headers = {
                            'auth-token':token,
                            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'
                }
                req = requests.post(timeout=120,url=ANUVAAD_UPLOADFILE_URL,files=uploadfiles_body,headers=headers)
                logger.debug(req.status_code)
                logger.debug(req.json())
                req.raise_for_status()  # Check for HTTP errors
                break  # Successful request, exit the loop
            except requests.exceptions.RequestException as e:
                logger.debug(f"Retry {retry_count + 1}/{max_retries}: {e}")
                time.sleep(retry_delay)

        if req.status_code >=200 and req.status_code <=204:
            file_id = req.json()["data"]
            return file_id
        else:
            return None

    def get_status_of_jobs(self,jobs,token):
        # hit upload_file api and fetch file_id
        logger.debug("Performing Bulk Search")
        bulk_body = {
            "offset": 0,
            "limit": 751,
            "jobIDs": jobs,
            "taskDetails": True,
            #"workflowCodes": ["DP_WFLOW_FBT", "WF_A_FCBMTKTR", "DP_WFLOW_FBTTR", "WF_A_FTTKTR"],
            "userIDs": []
        }

        for retry_count in range(max_retries):
            try:
                time.sleep(SLEEP_TIME)
                headers = {
                            'auth-token':token,
                            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'
                }
                req = requests.post(timeout=300,url=ANUVAAD_BULK_URL,json=bulk_body,headers=headers)
                req.raise_for_status()  # Check for HTTP errors
                break  # Successful request, exit the loop
            except requests.exceptions.RequestException as e:
                logger.debug(f"Retry {retry_count + 1}/{max_retries}: {e}")
                time.sleep(retry_delay)

        if req.status_code >=200 and req.status_code <=204:
            data = []
            for i in req.json()["jobs"]:
                job_data = {
                    "jobID" : i["jobID"],
                    "status" : i["status"],
                }
                if "output" in i.keys() and len(i["output"])>0 and "outputFile" in i["output"][0].keys():
                    job_data["output"] = i["output"][0]["outputFile"]
                data.append(job_data)
            return data
        else:
            return None
        
    def translate(self,file_name,file_id,token):
        # Perform translation
        logger.debug(f"Performing Translation {file_id}")
        asyncwf_body ={
                        "workflowCode": "WF_A_FCBMTKTR",
                        "jobName": file_name,
                        "jobDescription": "",
                        "files": [
                            {
                                "path": file_id,
                                "type": file_id.split()[-1],
                                "locale": "en",
                                "model": {
                                    "uuid": "fd4963c5-1ce8-4980-85c2-483fa9c59e5d",
                                    "is_primary": True,
                                    "model_id": 104,
                                    "model_name": "English-Tamil IndicTrans Model-1",
                                    "source_language_code": "en",
                                    "source_language_name": "English",
                                    "target_language_code": "ta",
                                    "target_language_name": "Tamil",
                                    "description": "AAI4B en-ta model-1(indictrans/fairseq)",
                                    "status": "ACTIVE",
                                    "connection_details": {
                                        "kafka": {
                                            "input_topic": "KAFKA_AAI4B_NMT_TRANSLATION_INPUT_TOPIC",
                                            "output_topic": "KAFKA_AAI4B_NMT_TRANSLATION_OUTPUT_TOPIC"
                                        },
                                        "translation": {
                                            "api_endpoint": "AAIB_NMT_TRANSLATE_ENDPOINT",
                                            "host": "AAI4B_NMT_HOST"
                                        },
                                        "interactive": {
                                            "api_endpoint": "AAIB_NMT_IT_ENDPOINT",
                                            "host": "AAI4B_NMT_HOST"
                                        }
                                    },
                                    "interactive_translation": True
                                },
                                "context": "JUDICIARY",
                                "modifiedSentences": "a"
                            }
                        ]
                    }
        
        for retry_count in range(max_retries):
            try:
                time.sleep(SLEEP_TIME)
                headers = {
                            'auth-token':token,
                            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'
                }
                req = requests.post(timeout=120,url=ANUVAAD_ASYNCWF_URL,json=asyncwf_body,headers=headers)
                req.raise_for_status()  # Check for HTTP errors
                break  # Successful request, exit the loop
            except requests.exceptions.RequestException as e:
                logger.debug(f"Retry {retry_count + 1}/{max_retries}: {e}")
                time.sleep(retry_delay)

        if req.status_code >=200 and req.status_code <=204:
            resp = req.json()
            return resp["jobID"],resp["startTime"]
        else:
            return None

    def digitize(self,file_name,file_id,token):
        # Perform digitization
        logger.debug("Performing Digitization")
        asyncwf_body ={
            "workflowCode": WORKFLOW_CODE,
            "jobName": file_name,
            "files": [
                {
                "path": file_id,
                "type": file_id[-3:],
                "locale": SOURCE_LANG_CODE,
                "config": {
                    "OCR": {
                    "line_layout": "False",
                    "option": "HIGH_ACCURACY",
                    "language": SOURCE_LANG_CODE,
                    "source_language_name": SOURCE_LANG_NAME
                    }
                }
                }
            ]
        }

        for retry_count in range(max_retries):
            try:
                time.sleep(SLEEP_TIME)
                headers = {
                            'auth-token':token,
                            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'
                }
                req = requests.post(timeout=120,url=ANUVAAD_ASYNCWF_URL,json=asyncwf_body,headers=headers)
                req.raise_for_status()  # Check for HTTP errors
                break  # Successful request, exit the loop
            except requests.exceptions.RequestException as e:
                logger.debug(f"Retry {retry_count + 1}/{max_retries}: {e}")
                time.sleep(retry_delay)

        if req.status_code >=200 and req.status_code <=204:
            resp = req.json()
            return resp["jobID"],resp["startTime"]
        else:
            return None
        

    def document_export(self,user_id,record_id,token):
        logger.debug("Performing Document Export")
        payload = json.dumps({
        "record_id": record_id,
        "user_id": user_id,
        "file_type": "pdf"
        })
        headers = {
        'auth-token': token,  
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Content-Type': 'application/json',
        }

        for retry_count in range(max_retries):
            try:
                time.sleep(SLEEP_TIME)
                logger.debug(payload)
                response = requests.request("POST", ANUVAAD_DOCUMENT_EXPORTER, headers=headers, data=payload)
                response.raise_for_status()  # Check for HTTP errors
                break  # Successful request, exit the loop
            except requests.exceptions.RequestException as e:
                logger.debug(f"Retry {retry_count + 1}/{max_retries}: {e}")
                time.sleep(retry_delay)

        if response.status_code >=200 and response.status_code <=204:
            logger.debug("Document Export",response.json())
            return response.json()["translated_document"]
        else:
            return None

    def download_file(self,download_path,token):
        logger.debug("Performing File Download")
        url = ANUVAAD_SERVE_FILE + download_path
        headers = {
                            'auth-token':token,
                            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'
                }

        for retry_count in range(max_retries):
            try:
                time.sleep(SLEEP_TIME)
                response = requests.request("GET", url, headers=headers)
                response.raise_for_status()  # Check for HTTP errors
                break  # Successful request, exit the loop
            except requests.exceptions.RequestException as e:
                logger.debug(f"Retry {retry_count + 1}/{max_retries}: {e}")
                time.sleep(retry_delay)

        if response.status_code >=200 and response.status_code <=204:
            return response.content
        else:
            return None

    def download_source_file(self,fileid,userid,token):
        # Download Source File
        logger.debug("Download Source File")
        url = f"{ANUVAAD_SOURCE_FILE_DOWNLOAD}?filename={fileid}&userid={userid}"
        headers = {
                            'auth-token':token,
                            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'
                }
        try:
            time.sleep(SLEEP_TIME)
            response = requests.request("GET", url, headers=headers)
            logger.debug(response.status_code)
            if response.status_code >=200 and response.status_code <=204:
                return response.content
            else:
                return None
        except Exception as e: 
            raise ValueError('error while exporting document : '+str(e))

    def fetch_content(self,record_id,token):
        # Perform Fetch Content
        logger.debug("Perform Fetch Content")
        record_id = record_id.replace('%7C','|')
        url = f"{ANUVAAD_FETCH_CONTENT}?record_id={record_id}&start_page=0&end_page=0"
        headers = {
                            'auth-token':token,
                            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'
                }
        for retry_count in range(max_retries):
            try:
                time.sleep(SLEEP_TIME)
                response = requests.request("GET", url, headers=headers)
                response.raise_for_status()  # Check for HTTP errors
                break  # Successful request, exit the loop
            except requests.exceptions.RequestException as e:
                logger.debug(f"Retry {retry_count + 1}/{max_retries}: {e}")
                time.sleep(retry_delay)


        if response.status_code >=200 and response.status_code <=204:
            return response.json()
        else:
            return None

    def download_translated_docx_file(self,fname,jobId,jobName,token):
        # Download Translated DOCX File
        logger.debug("Download Translated DOCX File")
        payload = json.dumps({
                    "fname": fname,
                    "jobId": jobId,
                    "jobName": jobName,
                    "authToken": token
                    })
        headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'auth-token': token,
        }

        for retry_count in range(max_retries):
            try:
                time.sleep(SLEEP_TIME)
                response = requests.request("POST", ANUVAAD_TRANSLATED_DOCX_DOWNLOAD, headers=headers, data=payload)
                response.raise_for_status()  # Check for HTTP errors
                break  # Successful request, exit the loop
            except requests.exceptions.RequestException as e:
                logger.debug(f"Retry {retry_count + 1}/{max_retries}: {e}")
                time.sleep(retry_delay)

        if response.status_code >=200 and response.status_code <=204:
            return response.content
        else:
            return None
