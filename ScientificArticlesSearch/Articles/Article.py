import datetime

'''
    format souhaite :

    "mot_cles": [],
    "auteurs": [],
    "references_bibliographique": [],
    "titre": "",
    "resume": "",
    "text_integral": "",
    "url": "",
    "date_de_publication": ?? null

'''


class Article:
    
    titre : str 
    resume : str
    texteIntegral : str  
    url : str
    authors : list 
    mots_cles : list 
    referencesBibliographiques : list
    dateDePublication : datetime 

    def __init__(self):
        pass

    def __init__(self,titre='',resume='',texteIntegral='',url='',dateDePublication=None,mot_cles=[],referencesBibliographiques=[],authors=[]):
        self.titre = titre
        self.resume = resume
        self.texteIntegral = texteIntegral
        self.url = url
        self.dateDePublication = dateDePublication
        self.mots_cles = mot_cles
        self.referencesBibliographiques = referencesBibliographiques
        self.authors = authors

