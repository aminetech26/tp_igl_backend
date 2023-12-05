# TP IGL Backend

## Project Overview
une application web permettant aux utilisateurs authentifiés de rechercher des articles scientifiques. Les utilisateurs peuvent filtrer les résultats, afficher les détails des articles, y compris le texte intégral en formats texte et PDF, et sauvegarder leurs articles préférés. Les administrateurs peuvent gérer les modérateurs et lancer des opérations d'upload d'articles scientifiques depuis des fichiers PDF. Après l'upload, les modérateurs peuvent vérifier et corriger les informations extraites à partir des articles PDF.

# Getting Started
## Prerequisites

* python
* pip
  
## Installation
1-Clone the repository.

```bash
git clone https://github.com/khaledbenmachiche/tp_igl_backend
cd tp_igl_backend
```
2-Install dependencies.

```bash
python -m venv env
source venv/bin/activate   # On Windows, use env\Scripts\activate
pip install -r requirements.txt
```
-Additionally, you might need to configure your database settings in the `settings.py` file and perform migrations accordingly.

3-Start the development server.

```bash
python manage.py runserver
```

## Contributing


1- Create a new branch for your feature or bug fix.

```bash
git checkout -b feature/my-feature
```
2- Make your changes and commit them with a clear message.

```bash
git commit -m "Add new feature"
```
3- Push your branch to the repository.

```bash
git push origin feature/my-feature
```
4- Create a pull request to the main branch of the repository.

-Remember to update the `requirements.txt` file with the necessary Django and other package versions used in your project.
    
  ```bash
  pip freeze > requirements.txt
  ```


