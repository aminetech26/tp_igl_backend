from ..google_drive.google_drive_api_handler import GoogleDriveAPIHandler
from .grobid_client import GrobidClient 
from .article_grobid_scrapper import parse_grobid_tei
import os
from io import BytesIO, FileIO
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from django.conf import settings
from ..serializers import ArticleSerializer


class GrobidScrapperManager:
    def __init__(self):
        self.drive_manager = GoogleDriveAPIHandler(
            settings.CLIENT_SECRET_FILE,
            settings.API_NAME,
            settings.API_VERSION,
            settings.SCOPES,
        )
        self.grobid_client = GrobidClient(config_path="./config.json")
        self.download_path = os.path.join(settings.MEDIA_ROOT, 'EchantillonsArticlesScrapping')
        self.results_directory = os.path.join(settings.MEDIA_ROOT, 'ScrapingResults')
        self.scraped_files_file_id = "1mzuTxnBquYkH0JdA93bXayPMF578BAKW"
        self.folder_id = "1GaKJSn08mD7tcd3VuR9kGvJXXII6C5iB"
    
    def _download_scrapping_folder(self):
        processed_files = self.drive_manager.get_file_content(self.scraped_files_file_id).splitlines()
        results = self.drive_manager.list_files(self.folder_id)
        print(results)
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        
        downloaded_files = [file for file in os.listdir(self.download_path) if (file.endswith(".pdf")) and os.path.isfile(os.path.join(self.download_path, file))]
        for file in results:
            file_name = file.get('name')
            file_id = file.get('id')

            if file_name == 'scraped_files.txt':
                print(f"Skipping the file: {file_name}")
                continue

            if file_name in processed_files:
                print(f"Le fichier {file_name} a déjà été traité. Skipping...")
            else:
                if file_name not in downloaded_files:
                    request = self.drive_manager.get_file_content_request(file_id)
                    file_path = os.path.join(self.download_path, file_name)
                    fh = FileIO(file_path, mode='wb')
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        print(f"Download {int(status.progress() * 100)}%.")
                else:
                    print("Already downloaded file!")
                    
                    
    @staticmethod
    def save_article_to_database(article):
        serializer = ArticleSerializer(data=article)
        
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
        else:
            errors = serializer.errors
            return f"Error while saving article to database. Errors: {errors}"
        
    def _scrape_articles_data(self):
        results = self.drive_manager.list_files(self.folder_id)
        processed_files = []
        processed_files = self.drive_manager.get_file_content(self.scraped_files_file_id).splitlines()
        for file in results:
            file_name = file.get('name')
            file_id = file.get('id')

            if file_name == 'scraped_files.txt':
                print(f"Skipping the file: {file_name}")
            else:
                tei_files = [
                    os.path.splitext(file)[0].replace(".grobid.tei", "").replace(".grobid", "")  # Extract file name without extension
                    for file in os.listdir(self.results_directory)
                    if (file.endswith(".grobid.tei.xml") or file.endswith(".grobid.tei")) and os.path.isfile(os.path.join(self.results_directory, file))
                ]

                if((file_name.replace(".pdf", "") in tei_files) and (file_name not in processed_files)):
                    for filename in os.listdir(self.results_directory):
                        if((filename.replace(".grobid.tei", "").replace(".grobid", "").replace(".xml", "")) == (file_name.replace(".pdf", ""))):
                            print(filename)
                            try:
                                file_metadata = self.drive_manager.get_file_metadata(file_id)
                                public_url = file_metadata.get('webContentLink') 
                                article = parse_grobid_tei(filename, public_url,self.results_directory)
                                error = self.save_article_to_database(article)
                                print(error)
                                break
                                processed_files.append(file_name)
                                updated_content = '\n'.join(processed_files)
                                media = MediaIoBaseUpload(BytesIO(updated_content.encode('utf-8')), mimetype='text/plain', resumable=True)
                                file_to_update = self.drive_manager.service.files().update(fileId=self.scraped_files_file_id, media_body=media).execute()
                                print(f"File {file_name} has been scraped successfully!")
                            except Exception as e:
                                print(f"Error processing {filename}: {e}")                    
                else:
                    print(f'Failed after multiple attempts.Error or already have been scraped | {file_name} has not been updated please retry again!!')
        
    def run_scrapper(self):
        self._download_scrapping_folder()
        self.grobid_client.process("processFulltextDocument", self.download_path, output=self.results_directory, consolidate_citations=True, tei_coordinates=True, force=True)
        self._scrape_articles_data() 