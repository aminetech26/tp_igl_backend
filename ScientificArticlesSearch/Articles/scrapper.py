class Scrapper:
    def __init__(self, file_path):
        self.file_path = file_path
        
    
    def run(self):
        print('Running scrapper...')
        print(f'File path: {self.file_path}')