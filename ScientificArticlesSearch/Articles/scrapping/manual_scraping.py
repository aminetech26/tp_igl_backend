import re
from .multi_column import column_boxes


keywords_list = ["Keywords: ","Keywords", "Key Word", "Keywords—", "Keywords:", "Key terms", "Main points","Keywords :","Key words:"]
abstract_start_keywords = ["1 ABSTRACT","1  ABSTRACT","Abstract", "Abstract——", "Abstract","Summary","abstract","ABSTRACT","ABSTRACT."," ABSTRACT_"," Abstract:"," ABSTRACT"," ABSTRACT."," ABSTRACT_"," Abstract:"]
abtract_stop_words = ["Categories and Subject Descriptors","","2 USE CASES","CCS CONCEPTS","Index Terms","Keywords: ","Introduction", "I. Introduction","Keywords", "Key Word", "Keywords—", "Keywords:", "Key terms", "Main points","Keywords :","Key words:","I."]
keywords_stop_words=["1. ","I. Introduction", "Introduction","I. "]
text_start_keywords = ["I. Introduction","1. Introduction","I. Introduction", "Introduction"]
text_end_keywords = ["REFERENCES","REFERENCES "," REFERENCES", "References","references"," REFERENCES", " References"," references","REFERENCES:", "References:","references:","REFERENCES"]
reference_start_keywords = ["REFERENCES","REFERENCES", "References","references"," REFERENCES", " References"," references","REFERENCES:", "References:","references:","References "," References"," References ","References",]
reference_end_keywords = ["Appendix", "APPENDIX"]

def find_abstract(doc, abstract_markers, abstract_stop_words):
    page_text = doc[0].get_text()  # Get text from the first page

    # Combine abstract markers into a regex pattern
    abstract_markers_pattern = "|".join(map(re.escape, abstract_markers))

    # Combine abstract stop words into a regex pattern
    abstract_stop_words_pattern = "|".join(map(re.escape, abstract_stop_words))

    # Construct the regex pattern to capture the abstract
    pattern = re.compile(fr'({"|".join(abstract_markers_pattern)})\s*(.*?)\s*({"|".join(abstract_stop_words_pattern)})', re.IGNORECASE | re.DOTALL)

    match = pattern.search(page_text)
    if match:
        abstract_text = match.group(2).strip()
        return f"Abstract:\n{abstract_text}\n\n"

def find_keywords(text, keywords_list):
    for keyword in keywords_list:
        match = re.search(fr"\s*{keyword}\s*:?\s*", text, flags=re.IGNORECASE)
        if match:
            keyword_start = match.start()
            for stop_word in keywords_stop_words:
                stop_index = text.find(stop_word, keyword_start)
                if stop_index != -1:
                    keywords_text = text[keyword_start:stop_index]
                    return keywords_text
            return text[keyword_start:]
    return None

abstract_found = False
keywords_found = False

def extract_text_between_markers(doc, start_keywords, end_keywords):
    # Combine start keywords into a regex pattern for finding the start marker
    start_pattern = "|".join(re.escape(keyword) for keyword in start_keywords)
    start_regex = re.compile(start_pattern, re.IGNORECASE)

    # Combine end keywords into a regex pattern for finding the end marker
    end_pattern = "|".join(fr'\b{re.escape(keyword)}\b' for keyword in end_keywords)
    end_regex = re.compile(end_pattern)

    # Join all the text from pages into a single string
    full_text = "\n".join(page.get_text() for page in doc)

    # Find the starting match
    start_match = start_regex.search(full_text)
    if start_match:
        start_index = start_match.start()
    else:
        return None  # Start marker not found

    # Find the ending match after the start index
    end_match = end_regex.search(full_text[start_index:])
    if end_match:
        end_index = end_match.start() + start_index
    else:
        return None  # End marker not found

    # Extract text between start and end indices
    extracted_text = full_text[start_index:end_index].strip()
    return extracted_text

def extract_references(doc, start_keywords, end_keywords):
    references = []
    start_index = None
    end_found = False

    # Constructing exact case-sensitive patterns for start keywords
    start_pattern = "|".join(fr'\b{re.escape(keyword)}\b' for keyword in start_keywords)
    start_regex = re.compile(start_pattern)

    # Combine end keywords into a regex pattern for finding the end marker
    end_pattern = "|".join(fr'\b{re.escape(keyword)}\b' for keyword in end_keywords)
    end_regex = re.compile(end_pattern)

    # Find the starting index in the document
    for page in doc:
        text = page.get_text()
        for keyword in start_keywords:
            if re.search(fr'\b{re.escape(keyword)}\b', text):
                start_index = text.find(keyword)
                if start_index != -1:
                    break
        if start_index is not None and start_index != -1:
            break

    if start_index is None or start_index == -1:
        return None

    # Search for references within the defined section
    capturing = False
    for page in doc:
        text = page.get_text()
        if start_index >= 0:
            extracted_text = text[start_index:]

            lines = extracted_text.split('\n')
            reference = ''
            for line in lines:
                line = line.strip()

                # Check for the start of a reference
                if start_regex.search(line):
                    capturing = True

                # Check for reference pattern only if capturing is True
                if capturing:
                    if re.match(r'^\[\d+\]', line):
                        references.append(reference.strip())
                        reference = line
                    else:
                        reference += ' ' + line
                
                # Check for end keywords to stop capturing references
                if any(end_regex.search(line) for keyword in end_keywords):
                    capturing = False
                    break

            if capturing:
                references.append(reference.strip())
                break
    if references:
        references.pop(0)

    return references