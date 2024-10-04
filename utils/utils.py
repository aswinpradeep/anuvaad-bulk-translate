import pandas as pd
import re
import requests
from urllib.parse import urlparse, parse_qs
import boto3
from config.config import *
from config.credentials import *

s3_client = None

class Utilities():

    def instantiate_s3_client(self):
        global s3_client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_session_token=AWS_SESSION_TOKEN
        )

    def get_s3_client(self):
        if s3_client is None:
            self.instantiate_s3_client()
        return s3_client

    def upload_s3_client(self,upload_filepath,upload_filename,original_filename):
        try:
            print("Uploading to S3")
            print(f"upload file path : {upload_filepath}")
            print(f"upload file name : {upload_filename}")
            original_filename = original_filename.replace("_digitized","")
            print(f"original file name : {original_filename}")
            s3 = self.get_s3_client()
            s3.upload_file(upload_filepath, BUCKET_NAME, upload_filename)
            upload_url = "https://anuvaad-parallel-corpus.s3-us-west-2.amazonaws.com/"+upload_filename
            df = pd.read_excel("./data_input/input.xlsx")
            index_to_update = df[df.iloc[:, 6] == original_filename].index
            df.iloc[index_to_update, 1] = upload_url
            df.to_excel("."+DATA_INPUT_FILE, index=False)
        except Exception as e:
            print(f"Unable to upload file, exception {e}")

    def download_files(self):
        df = pd.read_excel("./data_input/input.xlsx")

        df["Filename"] = ""

        for index, row in df.iterrows():
            i = row[0]
            if(self.identify_link_type(i)) == "Google Drive":
                # Google Drive link
                google_drive_link = i
                # Extract file ID from the link
                file_id = re.findall(r'/d/([a-zA-Z0-9_-]+)', google_drive_link)[0]
                # Get file metadata
                metadata_url = f"https://drive.google.com/uc?id={file_id}"
                response = requests.get(metadata_url)
                content_disposition = response.headers.get('content-disposition')
                # Extract the filename from content disposition
                filename = re.findall(r'filename="(.+)"', content_disposition)[0]
                # Construct the direct download link
                direct_download_link = f"https://drive.google.com/uc?id={file_id}"
                # Download the file
                response = requests.get(direct_download_link)
                # Save the file with the extracted filename
                filename = "./input/"+filename
                with open(filename, 'wb') as f:
                    f.write(response.content)
                df.at[index, "Filename"] = filename.split('/')[-1]      
                print(f"Downloaded file: {filename}")
            elif(self.identify_link_type(i)) == "S3":
                response = requests.get(i)
                filename = "./input/"+i.split('/')[-1]
                with open(filename, 'wb') as f:
                    f.write(response.content)
                df.at[index, "Filename"] = filename.split('/')[-1]        
                print(f"Downloaded file to {filename}")   
        df.to_excel("./data_input/input.xlsx", index=False)  

    def identify_link_type(self,link):
        if re.match(r'^https://drive\.google\.com/', link):
            return 'Google Drive'
        elif re.match(r'^https://.*s3.*\.amazonaws\.com/', link):
            return 'S3'
        else:
            return 'Other'    