from loguru import logger
logger.add("info.log")

#URLs
ANUVAAD_LOGIN_URL = "https://anuvaad-auth.tarento.com/anuvaad/user-mgmt/v1/users/login"
ANUVAAD_AUTHSEARCH_URL = "https://anuvaad-auth.tarento.com/anuvaad/user-mgmt/v1/users/auth-token-search"
ANUVAAD_UPLOADFILE_URL = "https://anuvaad-auth.tarento.com/anuvaad-api/file-uploader/v0/upload-file"
ANUVAAD_BULK_URL = "https://anuvaad-auth.tarento.com/anuvaad-etl/wf-manager/v1/workflow/jobs/search/bulk"
ANUVAAD_ASYNCWF_URL  = "https://anuvaad-auth.tarento.com/anuvaad-etl/wf-manager/v1/workflow/async/initiate"
ANUVAAD_DOCUMENT_EXPORTER = "https://anuvaad-auth.tarento.com/anuvaad-etl/document-converter/v0/document-exporter"
ANUVAAD_SERVE_FILE = "https://anuvaad-auth.tarento.com/anuvaad-api/file-uploader/v0/serve-file?filename="
ANUVAAD_SOURCE_FILE_DOWNLOAD = "https://anuvaad-auth.tarento.com/anuvaad-api/file-uploader/v0/download-file"
ANUVAAD_TRANSLATED_DOCX_DOWNLOAD = "https://anuvaad-auth.tarento.com/anuvaad-etl/anuvaad-docx-downloader/v0/download-docx"
ANUVAAD_FETCH_CONTENT = "https://anuvaad-auth.tarento.com/anuvaad/content-handler/v0/fetch-content"

#Other configs
INPUT_DIRECTORY = "/input/"
SOURCE_LANG_CODE = "en"
SOURCE_LANG_NAME = "English"
TARGET_LANG_CODE = "hi"
TARGET_LANG_NAME = "Hindi"
WORKFLOW_CODE = "WF_A_FCWDLDBSOD15GVOTK"
#WORKFLOW_CODE = "WF_A_FCWDLDBSOD20TESOTK"
BULK_WAIT_TIME = 25
DATA_INPUT_FILE = "/data_input/input.xlsx"
# INPUT_TYPE = "EXCEL"
INPUT_TYPE = "FILE"
BUCKET_NAME = 'anuvaad-parallel-corpus'
MAX_DIGITIZATION_UPLOADS = 2
MAX_TRANSLATION_UPLOADS = 2
SLEEP_TIME = 5


#MongoDB
mongo_server_host = 'mongodb://localhost:27017/?readPreference=primary&ssl=false'
mongo_wfm_db = 'bulk_script_db'
mongo_wfm_jobs_col = 'bulk_script_collection_1'
