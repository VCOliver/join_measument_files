import os
import pprint
from chardet import detect

MEASUREMENTS_PATH = 'measurements/test_240202'

printer = pprint.PrettyPrinter()
pp = printer.pprint

def get_file_encoding(file_name: str) -> str:
    file_path = f'{MEASUREMENTS_PATH}/{file_name}'
    
    with open(file_path, 'rb') as file:
        result = detect(file.read())
       
    encoding = result['encoding'] if result['encoding'] != 'ascii' else 'utf-8' #returns utf-8 if encoding in ASCII
       
    print(f"The file's encoding is [{encoding}] with {result['confidence']*100}% confidence.") 
    return encoding

if __name__ == '__main__':
    encoding = get_file_encoding('test_1.txt')
    
    