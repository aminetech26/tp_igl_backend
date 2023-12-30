class Auteur:
    nom: str
    institution: str

    def __init__(self, nom: str = '', institution: str = ''):
        self.nom = nom
        self.institution = institution