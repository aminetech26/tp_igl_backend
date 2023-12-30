import ast
import requests
from googleapiclient.http import MediaIoBaseDownload
import fitz
from .date_exractor import extract_date_from_text
from .manual_scraping import extract_text_between_markers, extract_references
import io
from .Article import Article
from .Author import Author
import time

class Scrapper:
    def __init__(self):
        self.article = Article()
    #SCRAPING MANUEL CONFIG
    text_start_keywords = ["1. Motivation and significance","I. Introduction","1. Introduction","I. Introduction", "Introduction"]
    text_end_keywords = ["REFERENCES","REFERENCES "," REFERENCES", "References","references"," REFERENCES", " References"," references","REFERENCES:", "References:","references:","REFERENCES"]
    reference_start_keywords = ["REFERENCES","REFERENCES", "References","references"," REFERENCES", " References"," references","REFERENCES:", "References:","references:","References "," References"," References ","References",]
    reference_end_keywords = ["Appendix", "APPENDIX"]


    def getArticleFromUrl(self,service,file_name,file_id,url):
       
        #REQUEST CONFIG
        RETRY_ATTEMPTS = 3  
        ATTEMPT = 1
        ALL_SUCCESS = False

        self.article.url = url
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
                        print(f"({champ}):")
                        print(f"Result ({champ}): {response.json()['content']}")
                        if champ == "titre":
                            self.article.titre = response.json()['content']
                        elif champ == "resume":
                            self.article.resume = response.json()['content']
                        elif champ == "mots-cles":
                            self.article.mots_cles = [mot.strip() for mot in response.json()['content'].split(',')]
                        elif champ == "date-de-publication":
                            date_str = response.json()['content']
                            dateDePublication = extract_date_from_text(date_str)
                            self.article.dateDePublication = dateDePublication
                        elif champ == "institutions":
                            response_content = response.text
                            # Use ast.literal_eval to safely parse the string into a dictionary
                            institutions_dict = ast.literal_eval(response_content)
                            if isinstance(institutions_dict, dict):
                                for author_name, institution in institutions_dict.items():
                                    print(author_name)
                                    print(institution)
                                    author = Author(nom=author_name.strip(), institution=institution.strip())
                                    self.article.authors.append(author)

                                print(self.article.authors)                          

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
            fh = io.FileIO(file_name, mode='wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")
            print("Download Complete!")
            if done:
                doc = fitz.open(file_name)
                text = extract_text_between_markers(doc,self.text_start_keywords,self.text_end_keywords)
                self.article.texteIntegral = text
                references = extract_references(doc,self.reference_start_keywords,self.reference_end_keywords)
                self.article.referencesBibliographiques = references
                return self.article
        else:
            return None