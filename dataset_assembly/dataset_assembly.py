import csv

from text_extracter import TextExtracter
from os import listdir
from os.path import isfile, join, exists

class DatasetAssembly:
    
    def __init__(self, dir:str, extracter:TextExtracter):
        self.dir = dir
        self.extracter = extracter
        
    def extract(self, doc_path:str) -> str|None:
        if not exists(doc_path): return None
        text = self.extracter.extract(doc_path)
        return text
    
    def extract_from_List(self, file_paths:str) -> list|None:
        extraction_list = list(map(self.extract, file_paths))
        return extraction_list
    
    def generate_csv(self, dir_path:str, csv_name:str = 'data.csv'):
        files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
        categories = [f.split('.')[0] for f in files]
        
        full_files = [f'{dir_path}\{f}' for f in files]
        extraction_list = self.extract_from_List(full_files)
        
        dict_to_csv = [{'text': t, 'category': c} for t, c in zip(extraction_list, categories)]
        fields = ['text', 'category']
        
        with open(csv_name, 'w', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            writer.writerows(dict_to_csv)
    
if __name__ == '__main__':
    da = DatasetAssembly('', TextExtracter)
    res = da.generate_csv('dataset_assembly\data')