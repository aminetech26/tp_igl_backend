from Google import Create_Service
from googleapiclient.http import MediaIoBaseUpload
from io import *
from Scrapper import *

#ARTICLE RETRIEVAL AUTOMATION
CLIENT_SECRET_FILE = 'client_secret_808300273724-h05se6t7qe1ro4opie0sdkdj0bu3m5vd.apps.googleusercontent.com.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)

folder_id = "1GaKJSn08mD7tcd3VuR9kGvJXXII6C5iB"
scraped_files_drive_id = "10mUi2bDk-mnmJsWwMGX5EK1UH_NYpy8-"

results = service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    fields="files(id, name)"
).execute()

file_content = service.files().get_media(fileId=scraped_files_drive_id).execute()
scraped_files_content = file_content.decode('utf-8')
processed_files = scraped_files_content.splitlines()

for file in results.get('files', []):
    file_name = file.get('name')
    file_id = file.get('id')

    if file_name == 'scraped_files.txt':
        print(f"Skipping the file: {file_name}")
        continue

    if file_name in processed_files:
        print(f"Le fichier {file_name} a déjà été traité. Skipping...")
        continue
    else:
        request_body = {
            'role':'reader',
            'type':'anyone'
        }

        response_permission = service.permissions().create(
            fileId=file_id,
            body=request_body
        ).execute()
        response_share_link = service.files().get(
            fileId = file_id,
            fields = 'webViewLink'
        ).execute()
        file_metadata = service.files().get(fileId=file_id, fields='webContentLink').execute()
        public_url = file_metadata.get('webContentLink')        
        
        file_scrapper = Scrapper()
        article = file_scrapper.getArticleFromUrl(service,file_name,file_id,public_url)
        
        print("*****************************************")
        
        if article:
            for attribute, value in article.__dict__.items():
                print(f"{attribute}: {value}")
            processed_files.append(file_name)
            updated_content = '\n'.join(processed_files)
            media = MediaIoBaseUpload(BytesIO(updated_content.encode('utf-8')), mimetype='text/plain', resumable=True)
            file_to_update = service.files().update(fileId=scraped_files_drive_id, media_body=media).execute()
            print(f"File {file_name} updated successfully!")
        else:
            print(f'Failed after multiple attempts.{file_name} has not been uploaded please retry again!!')

        