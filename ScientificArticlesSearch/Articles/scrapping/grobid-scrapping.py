from grobid_client.grobid_client import GrobidClient
from Google import Create_Service
from googleapiclient.http import MediaIoBaseUpload
from io import *
from bs4 import BeautifulSoup
import subprocess
import time
import psutil
import os
#TODO : replace these two imports by the current strucutre of the models 
from Article import Article
from Author import Author
from datetime import datetime
import xml.etree.ElementTree as ET
import grobid_tei_xml
from date_exractor import *
from googleapiclient.http import MediaIoBaseDownload
import io

#DOCKER SERVER RUNNING CONFIG 

def is_grobid_running():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'java' in proc.info['name'] and '-jar' in proc.info['cmdline'] and 'grobid-core' in proc.info['cmdline']:
            return True
    return False

def start_grobid_server():
    subprocess.run(['docker', 'run', '--rm', '--init', '--ulimit', 'core=0', '-p', '8070:8070', 'grobid/grobid:0.8.0'])

def stop_grobid_server():
    command_output = subprocess.run(['docker', 'ps', '-q', '-f', 'ancestor=grobid/grobid'], capture_output=True, text=True)
    container_ids = command_output.stdout.splitlines()
    for container_id in container_ids:
        subprocess.run(['docker', 'stop', container_id])
    print('Server stopped succesfully!')

#############################

#GOOGLE DRIVE CONFIG
CLIENT_SECRET_FILE = 'client_secret_808300273724-h05se6t7qe1ro4opie0sdkdj0bu3m5vd.apps.googleusercontent.com.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']
service = Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)
#############################

#fonction utilitaire
def extract_folder_id(url):
    parts = url.split('/')
    for part in parts:
        if part.startswith('1') and len(part) == 33:
            return part
    return None
#############################

# Example URL - get url from user front (credentials)
url = "https://drive.google.com/drive/folders/1GaKJSn08mD7tcd3VuR9kGvJXXII6C5iB"
folder_id = extract_folder_id(url)
scraped_files_file_id = "1Hc7Oiwc-AaVVshOnY4Gf28_F2cW5P6Ct"
results_directory = "./ScrapingResults/"
download_path = './EchantillonsArticlesScrapping/'
#############################

#GOOGLE DRIVE FETCHING AND LISTING FILES
results = service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    fields="files(id, name)"
).execute()

file_content = service.files().get_media(fileId=scraped_files_file_id).execute()
scraped_files_content = file_content.decode('utf-8')
processed_files = scraped_files_content.splitlines()
#############################

if not os.path.exists(download_path):
    os.makedirs(download_path)
downloaded_files = [file for file in os.listdir(download_path) if (file.endswith(".pdf")) and os.path.isfile(os.path.join(download_path, file))]

def format_reference_bibliographique(citation) -> str:
        authors_str = ', '.join([author.full_name for author in citation.authors])
        title_str = f'"{citation.title}"' if citation.title else ''
        journal_info_str = f'{citation.journal} {citation.volume}({citation.issue}):{citation.pages}' if citation.journal else ''
        publication_info_str = f'{citation.publisher}, {citation.date}' if citation.publisher else ''
        doi_str = f'DOI: {citation.doi}' if citation.doi else ''
        reference_str = f"[{citation.index + 1}] {authors_str}. {title_str} {journal_info_str} {publication_info_str}. {doi_str}"

        return reference_str

#function to extract fields from .tei file
def parse_grobid_tei(file_name, public_url):
    file_path = f"{results_directory}/{file_name}"
    with open(file_path, 'r', encoding='utf-8') as file:
        tei_content = file.read()

    soup = BeautifulSoup(tei_content, 'lxml-xml')

    titre_element = soup.find('title', {'type': 'main'})
    titre = titre_element.text.strip() if titre_element else None

    print(f'Titre : {titre}')

    url = public_url

    resume_paragraphs = [p.text.strip() for p in soup.select('abstract p')]
    resume = ' '.join(resume_paragraphs)

    print(f'Résumé : {resume}')


    texte_integral = {}
    for div in soup.select('div'):
        head = div.find('head')
        paragraphs = div.select('p')

        if head is not None:
            head_text = head.text.strip()
            paragraph_texts = [p.text.strip() for p in paragraphs]
            texte_integral[head_text] = paragraph_texts

    print(f'Texte intégral : {texte_integral}')

    authors = []
    file_desc = soup.select_one('fileDesc')

    if file_desc:
        for author_elem in file_desc.select('author'):
            forename = author_elem.select_one('forename')
            surname = author_elem.select_one('surname')
            institution = author_elem.select_one('affiliation orgName')
            if forename and surname and institution:
                forename_text = forename.text.strip()
                surname_text = surname.text.strip()
                institution_text = institution.text.strip()
                nom = f"{forename_text} {surname_text}"
                author = Author(nom, institution_text)
                authors.append(author)

    for author in authors:
        print(f"Author: {author.nom}")
        print(f"Institution: {author.institution}")
        print("-----")

    mots_cles = []
    direct_keywords = soup.select('textClass > keywords')
    for direct_keyword in direct_keywords:
        term_elements = direct_keyword.select('term')
        if term_elements:
            mots_cles.extend(term.text.strip() for term in term_elements)
        else:
            mots_cles.append(direct_keyword.text.strip())
    print(mots_cles)

    print(f'Mots clés : {mots_cles}')


    doc = grobid_tei_xml.parse_document_xml(tei_content)
    citations = doc.citations

    references_bibliographiques = [format_reference_bibliographique(citation) for citation in citations]

    for reference in references_bibliographiques:
        print(reference)
    
    date_element = soup.select_one('date')
    date_str = date_element.text.strip() if date_element else None
    date_de_publication = extract_date_from_text(date_str)

    article = Article(titre, resume, texte_integral, url, authors, mots_cles, citations, date_de_publication)

    return article

#DOWNLOADING NEWLY ADDED (NON SCRAPED) FILES

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
        if file_name not in downloaded_files:
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(download_path + file_name, mode='wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")
            print("Download Complete!")
        else:
            print("Already downloaded file!")
            continue

#############################


#CHECKING IF GROBID SERVER IS RUNNING AND RUN IT OTHERWISE
        
if not is_grobid_running():
    print("GROBID server is not running. Starting GROBID...")
    start_grobid_server()
    time.sleep(30)

#############################

#SCRAPING FILES - part one
client = GrobidClient(config_path="./config.json")
client.process("processFulltextDocument", "./EchantillonsArticlesScrapping", output="./ScrapingResults/", consolidate_citations=True, tei_coordinates=True, force=True)
stop_grobid_server
#############################

#CHECKING FOR FILES SUCCESFULLY SCRAPED
for file in results.get('files', []):
    file_name = file.get('name')
    file_id = file.get('id')
    if file_name == 'scraped_files.txt':
        print(f"Skipping the file: {file_name}")
        continue
    else:

        tei_files = [
            os.path.splitext(file)[0].replace(".grobid.tei", "").replace(".grobid", "")  # Extract file name without extension
            for file in os.listdir(results_directory)
            if (file.endswith(".grobid.tei.xml") or file.endswith(".grobid.tei")) and os.path.isfile(os.path.join(results_directory, file))
        ]

        if((file_name.replace(".pdf", "") in tei_files) and (file_name not in processed_files)):
            
            for filename in os.listdir(results_directory):
                if((filename.replace(".grobid.tei", "").replace(".grobid", "").replace(".xml", "")) == (file_name.replace(".pdf", ""))):
                    try:
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
                        article = parse_grobid_tei(filename, public_url)
                        print(f"Processing {filename} - Article Title: {article.titre}")
                        processed_files.append(file_name)
                        updated_content = '\n'.join(processed_files)
                        media = MediaIoBaseUpload(BytesIO(updated_content.encode('utf-8')), mimetype='text/plain', resumable=True)
                        file_to_update = service.files().update(fileId=scraped_files_file_id, media_body=media).execute()
                        
                        print(f"File {file_name} has been scraped successfully!")
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                                    
        else:
            print(f'Failed after multiple attempts.Error or already have been scraped | {file_name} has not been updated please retry again!!')

#############################