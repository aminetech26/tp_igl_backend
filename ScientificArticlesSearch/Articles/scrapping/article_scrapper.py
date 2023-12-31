from django.conf import settings
import ast
import requests
from googleapiclient.http import MediaIoBaseDownload
import fitz
from .date_exractor import extract_date_from_text
from .manual_scraping import extract_text_between_markers, extract_references
import io
import os
import time
import json

class ArticleScrapper:
    def __init__(self):
        self.article = {
            "mot_cles": [],
            "auteurs": [],
            "references_bibliographique": [],
            "titre": "",
            "resume": "",
            "text_integral": "",
            "url": "",
            "date_de_publication": None,
        }
        
    
    #SCRAPING MANUEL CONFIG
    text_start_keywords = ["1. Motivation and significance","I. Introduction","1. Introduction","I. Introduction", "Introduction"]
    text_end_keywords = ["REFERENCES","REFERENCES "," REFERENCES", "References","references"," REFERENCES", " References"," references","REFERENCES:", "References:","references:","REFERENCES"]
    reference_start_keywords = ["REFERENCES","REFERENCES", "References","references"," REFERENCES", " References"," references","REFERENCES:", "References:","references:","References "," References"," References ","References",]
    reference_end_keywords = ["Appendix", "APPENDIX"]

        

    def get_article_from_url(self,service,file_name,file_id,url):
        #REQUEST CONFIG
        RETRY_ATTEMPTS = 3  
        ATTEMPT = 1
        ALL_SUCCESS = False

        self.article["url"] = url
        prompts = {
        "titre":"Retourner le titre de cet article scientifique \"sans aucun texte supplémentaire et sans aucun préfixe dans la réponse\"",
        "authors":"Retourner la liste complete des noms et prenoms complets des autheurs ce cet article sous forme de liste separes par des virgules. \"sans aucun préfixe ou texte supplémentaire dans la réponse\"",
        "resume": "Veuillez fournir [la partie \"ABSTRACT\"] complet tel qu'il est dans l'article \"sans aucun texte supplémentaire et sans aucun préfixe dans la réponse\"",
        "mots-cles": "Retourner la liste des mots-clés [KEY-WORDS] dand cet article sous forme de liste separes par des virgules. \"sans aucun préfixe ou texte supplémentaire dans la réponse\"",
        "date-de-publication":"Veuillez extraire une date de publication depuis l'article. Si la date de publication spécifique n'est pas clairement indiquée, fournissez soit la date d'acceptation de l'article, soit la date de la conférence où l'article a été présenté. \"Si aucune date spécifique n'est clairement indiquée, veuillez fournir une date approximative basée sur le contenu de l'article, en utilisant une estimation raisonnable\". \"retourner uniquement la date sans aucun préfixe ou texte supplémentaire dans la réponse\"",
        "institutions": "Retournez tous les institutions auquels appartient tous les autheurs de cet article [les institutions qui apparaissent dans les references ne sont pas concernees]. la reponse doit etre sous forme d'un dictionnaire avec les auteurs de l'article comme clés et leurs institutions respectives comme valeurs. \"La reponse ne doit pas contenir un texte supplementaire ou un prefixe\""
        }

        headers = {
        'x-api-key': 'sec_GDq9Qk64F7CH5APLHZCn5GYEsEqTHh4X',
        'Content-Type': 'application/json'
        }

        data = {'url': url}
        url = f'https://api.chatpdf.com/v1/sources/add-url'
        
        print(data)
        while ATTEMPT <= RETRY_ATTEMPTS:
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                source_id = response.json()['sourceId']
                ALL_SUCCESS = True  

                for champ, prompt in prompts.items():
                    data = {
                        'sourceId': source_id,
                        'messages': [
                            {
                                'role': "user",
                                'content': prompt,
                            }
                        ]
                    }
                    response = requests.post('https://api.chatpdf.com/v1/chats/message', headers=headers, json=data)

                    if response.status_code == 200:
                        if champ == "titre":
                            self.article["titre"] = response.json()['content']
                        elif champ == "resume":
                            self.article["resume"] = response.json()['content']
                        elif champ == "mots-cles":
                            print(response.json()['content'].split(','))
                            self.article["mot_cles"] = [{"text": mot.strip()} for mot in response.json()['content'].split(',')]
                        elif champ == "date-de-publication":
                            date_str = response.json()['content']
                            date_de_publication = extract_date_from_text(date_str)
                            if date_de_publication is not None:
                                self.article["date_de_publication"] = date_de_publication.date()

                        elif champ == "institutions":
                            response_content = response.text
                            try:
                                institutions_dict = ast.literal_eval(response_content)
                            except (SyntaxError, ValueError) as e:
                                print(f"Error parsing content as a dictionary: {e}")
                                institutions_dict = {}
                            
                            if isinstance(institutions_dict, dict):
                                content_dict = institutions_dict.get('content', {})
                                try:
                                    content_dict = json.loads(content_dict)
                                except json.JSONDecodeError as e:
                                    print(f"Error decoding JSON: {e}")
                                    content_dict = {}
                                for author_name, institution in content_dict.items():
                                    author = {
                                        "nom": author_name.strip(),
                                        "institutions": [{"nom": institution.strip()}]
                                    }
                                    self.article["auteurs"].append(author)

                    else:
                        print(f"Attempt {ATTEMPT}/{RETRY_ATTEMPTS} - Retrying after 5 seconds...")
                        ALL_SUCCESS = False  # Une requête a échoué, ne pas mettre à jour le fichier
                        time.sleep(5)
                        break

                if ALL_SUCCESS:
                    break  
            else:
                print(f"Attempt {ATTEMPT}/{RETRY_ATTEMPTS} - Retrying after 5 seconds...")
                time.sleep(5)
                ATTEMPT += 1

        if ALL_SUCCESS:
            request = service.files().get_media(fileId=file_id)
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            fh = io.FileIO(file_path, mode='wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")
            print("Download Complete!")
            if done:
                doc = fitz.open(file_name)
                text = extract_text_between_markers(doc,self.text_start_keywords,self.text_end_keywords)
                if text is not None:
                    self.article["text_integral"] = text

                references = extract_references(doc,self.reference_start_keywords,self.reference_end_keywords)
                if references is not None:
                    self.article["references_bibliographique"] = [{ "nom" : reference } for reference in references]
                else:
                    self.article["references_bibliographique"] = []
                return self.article
        else:
            return None
        