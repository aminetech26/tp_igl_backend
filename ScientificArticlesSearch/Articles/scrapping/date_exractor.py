from dateutil import parser
import re

def extract_date_from_text(response_text):
    specific_date_match = re.search(r'(\d{1,2}\s*(?:[/-])\s*\d{1,2}\s*(?:[/-])\s*\d{4})', response_text)

    if specific_date_match:
        specific_date_str = specific_date_match.group(1)
        specific_date = parser.parse(specific_date_str, dayfirst=True, yearfirst=False)
        print("Specific Date of Publication:", specific_date)
        return specific_date
    else:
        month_mapping = {
            'janvier': 'January',
            'février': 'February',
            'mars': 'March',
            'avril': 'April',
            'mai': 'May',
            'juin': 'June',
            'juillet': 'July',
            'août': 'August',
            'septembre': 'September',
            'octobre': 'October',
            'novembre': 'November',
            'décembre': 'December'
        }
        month_year_match = re.search(r'(?:\d{1,2}\s*)?(\b(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s*\d{4})', response_text, flags=re.IGNORECASE)

        if month_year_match:
            month_year_str = month_year_match.group(1)
            
            for french_month, english_month in month_mapping.items():
                month_year_str = month_year_str.replace(french_month, english_month)

            date = parser.parse(month_year_str, fuzzy=True).date()
            return date
        else:
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}/\d{4}|\d{4})', response_text)

            if date_match:
                date_str = date_match.group(1)
                date = parser.parse(date_str, dayfirst=False, yearfirst=False).date()
                return date
            else:
                return None

