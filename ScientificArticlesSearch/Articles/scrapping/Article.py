import datetime
from typing import List
from .Auteur import Auteur


class Article:
    titre : str 
    resume : str
    text_integral : str  
    url : str
    auteurs : list 
    mot_cles : list 
    references_bibliographique : list
    date_de_publication : datetime 

    def __init__(
        self,
        titre: str = '',
        resume: str = '',
        texte_integral: str = '',
        url: str = '',
        date_de_publication: datetime.datetime = None,
        mots_cles: List[str] = [],
        references_bibliographiques: List[str] = [],
        auteurs: List[Auteur] = []
    ):
        self.titre = titre
        self.resume = resume
        self.texte_integral = texte_integral
        self.url = url
        self.date_de_publication = date_de_publication
        self.mots_cles = mots_cles
        self.references_bibliographiques = references_bibliographiques
        self.auteurs = auteurs

