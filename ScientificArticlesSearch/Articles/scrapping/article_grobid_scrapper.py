from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import grobid_tei_xml
from .date_exractor import extract_date_from_text
import os
import json

def format_reference_bibliographique(citation) -> str:
    authors_str = ', '.join([author.full_name for author in citation.authors])
    title_str = f'"{citation.title}"' if citation.title else ''
    journal_info_str = f'{citation.journal} {citation.volume}({citation.issue}):{citation.pages}' if citation.journal else ''
    publication_info_str = f'{citation.publisher}, {citation.date}' if citation.publisher else ''
    doi_str = f'DOI: {citation.doi}' if citation.doi else ''
    reference_str = f"[{citation.index + 1}] {authors_str}. {title_str} {journal_info_str} {publication_info_str}. {doi_str}"

    return reference_str

#function to extract fields from .tei file
def parse_grobid_tei(file_name, public_url, results_directory):
    article = {
        "mot_cles": [],
        "auteurs": [],
        "references_bibliographique": [],
        "titre": "",
        "resume": "",
        "text_integral": "",
        "url": "",
        "date_de_publication": None,
    }
    file_path = os.path.join(results_directory, file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        tei_content = file.read()

    soup = BeautifulSoup(tei_content, 'lxml-xml')

    titre_element = soup.find('title', {'type': 'main'})
    article['titre'] = titre_element.text.strip() if titre_element else None

    article['url'] = public_url

    resume_paragraphs = [p.text.strip() for p in soup.select('abstract p')]
    article['resume'] = ' '.join(resume_paragraphs)

    texte_integral = {}
    for div in soup.select('div'):
        head = div.find('head')
        paragraphs = div.select('p')

        if head is not None:
            head_text = head.text.strip()
            paragraph_texts = [p.text.strip() for p in paragraphs]
            texte_integral[head_text] = paragraph_texts
            
    article['text_integral'] = json.dumps(texte_integral)

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
                author = {
                    "nom": nom,
                    "institutions": [{
                        "nom": institution_text
                    }],
                }
                authors.append(author)

    direct_keywords = soup.select('textClass > keywords')
    for direct_keyword in direct_keywords:
        term_elements = direct_keyword.select('term')
        if term_elements:
            article['mot_cles'].extend({"text":term.text.strip()} for term in term_elements)
        else:
            article['mot_cles'].append({"text":direct_keyword.text.strip()})
            

    doc = grobid_tei_xml.parse_document_xml(tei_content)
    citations = doc.citations

    article['references_bibliographique'] = [{"nom":format_reference_bibliographique(citation)} for citation in citations]

    date_element = soup.select_one('date')
    date_str = date_element.text.strip() if date_element else None
    print(date_str)
    article['date_de_publication'] = extract_date_from_text(date_str)

    return article