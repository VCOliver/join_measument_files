import os
import pprint
from chardet import detect
import pandas as pd
from tabulate import tabulate
import sys

MEASUREMENTS_PATH = 'measurements/test_240202'
MEASUREMENTS_STATS_PATH = 'files_statistics'

printer = pprint.PrettyPrinter()
pp = printer.pprint

def get_file_encoding(file_name: str) -> str:
    file_path = f'{MEASUREMENTS_PATH}/{file_name}'
    
    with open(file_path, 'rb') as file:
        result = detect(file.read())
       
    encoding = result['encoding'] if result['encoding'] != 'ascii' else 'utf-8' #returns utf-8 if encoding in ASCII
       
    print(f"The file's encoding is [{encoding}] with {result['confidence']*100}% confidence.") 
    return encoding

def main(table_styling='rounded_outline'):
    encoding = get_file_encoding('test_1.txt')
    header = ['time', 'x', 'y', 'z']
    df = pd.read_csv(f'{MEASUREMENTS_PATH}/test_1.txt', sep='\t', decimal=',', encoding=encoding, header=None, names=header)
    
    if not os.path.exists(MEASUREMENTS_STATS_PATH):
        os.makedirs(MEASUREMENTS_STATS_PATH)
    file_stats = df.describe()
    file_path = f'{MEASUREMENTS_STATS_PATH}/test_1_stats.txt'
    
    table = tabulate(file_stats, headers='keys', tablefmt=table_styling, floatfmt=".7f")
    
    with open(file_path, 'w', encoding=encoding) as file:
        file.write(table)


if __name__ == '__main__':
    table_styling = None
    if len(sys.argv) > 1:
        table_styling = sys.argv[1]
        main(table_styling)
    else:  
        main()
    