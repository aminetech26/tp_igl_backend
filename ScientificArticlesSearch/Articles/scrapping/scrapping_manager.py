from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from Articles.scrapping.article_scrapper import ArticleScrapper 
from Articles.google_drive.google_drive_api_handler import GoogleDriveAPIHandler
from Articles.serializers import ArticleSerializer


class ScrappingManager:
    def __init__(self):
        self.drive_manager = GoogleDriveAPIHandler(
            'client_secret_808300273724-h05se6t7qe1ro4opie0sdkdj0bu3m5vd.apps.googleusercontent.com.json',
            'drive',
            'v3',
            ['https://www.googleapis.com/auth/drive']
        )
    
    def run_scrapper(self):
        folder_id = "1GaKJSn08mD7tcd3VuR9kGvJXXII6C5iB"
        scraped_files_drive_id = "1NSLtcXMzzsIuiYLpdqbhOkjEdHoYZ0mz"

        results = self.drive_manager.list_files(folder_id)
        scraped_files_content = self.drive_manager.get_file_content(scraped_files_drive_id)
        processed_files = scraped_files_content.splitlines()

        for file in results:
            file_name = file.get('name')
            file_id = file.get('id')

            if file_name == 'scraped_files.txt':
                print(f"Skipping the file: {file_name}")
                continue

            if file_name in processed_files:
                print(f"Le fichier {file_name} a déjà été traité. Skipping...")
            else:
                self.process_file(file_name, file_id, scraped_files_drive_id, processed_files)
    
    def process_file(self, file_name, file_id, scraped_files_drive_id, processed_files):
        article_scrapper = ArticleScrapper()

        public_url = self.drive_manager.get_web_content_link(file_id)
        article = article_scrapper.get_article_from_url(self.drive_manager.service, file_name, file_id, public_url)
        if article:
            self.save_article_to_data_base(article)
            processed_files.append(file_name)
            updated_content = '\n'.join(processed_files)
            
            self.drive_manager.update_scraped_files(scraped_files_drive_id, updated_content)
            print(f"File {file_name} updated successfully!")
        else:
            return f'Failed after multiple attempts. {file_name} has not been uploaded. Please retry again!!'
            
    def save_article_to_database(self,article):
        serializer = ArticleSerializer(data=article)
        
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
        else:
            return "Error while saving article to database"
        