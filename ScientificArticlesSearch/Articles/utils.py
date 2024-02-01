def extract_drive_folder_id(url:str)->str or None:
    parts = url.split('/')
    for part in parts:
        if part.startswith('1') and len(part) == 33:
            return part
    return None
