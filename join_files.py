import os
import pprint
from chardet import detect
import pandas as pd
from tabulate import tabulate, tabulate_formats
import sys
import numpy as np
from datetime import datetime

MEASUREMENTS_PATH = 'measurements/test_240202'
MEASUREMENTS_STATS_PATH = 'files_statistics'
SAMPLES_PER_LOOP = 16520 # The NI9234 takes 16520 samples than stop to save them in a .txt file
LOOPS_PER_FILE = 4

printer = pprint.PrettyPrinter()
pp = printer.pprint

def get_file_encoding(file_name: str) -> str:
    file_path = f'{MEASUREMENTS_PATH}/{file_name}'
    
    creation_time = os.stat(file_path)
    print(creation_time)
    
    with open(file_path, 'rb') as file:
        result = detect(file.read())
       
    encoding = result['encoding'] if result['encoding'] != 'ascii' else 'utf-8' #returns utf-8 if encoding in ASCII
       
    print(f"The file's encoding is [{encoding}] with {result['confidence']*100}% confidence.") 
    return encoding

def write_stats(df: pd.DataFrame, file_name: str, encoding='utf-8', table_styling='rounded_outline') -> None:
    if not os.path.exists(MEASUREMENTS_STATS_PATH):
        os.makedirs(MEASUREMENTS_STATS_PATH)
    file_stats = df.describe()
    count = str(int(file_stats.iloc[0, 1]))
    file_stats.drop('count', inplace=True)
    
    file_path = f'{MEASUREMENTS_STATS_PATH}/{file_name}'
    table = tabulate(file_stats, headers='keys', tablefmt=table_styling, floatfmt=".7f")
    with open(file_path, 'w', encoding=encoding) as file:
        file.write(table)
        file.write(f'\n\nNumber of measuments = {count}')

def get_mean_saving_time(df: pd.DataFrame) -> float:
    saving_time = 0    
    for i in range(1, LOOPS_PER_FILE):
        saving_time+= df.iloc[SAMPLES_PER_LOOP*i, 0] - df.iloc[SAMPLES_PER_LOOP*i-1, 0]
    saving_time = saving_time / (LOOPS_PER_FILE-1)
    
    return saving_time.round(6)

def main(table_styling):
    encoding = get_file_encoding('test_1.txt')
    header = ['time', 'x', 'y', 'z']
    df = pd.read_csv(f'{MEASUREMENTS_PATH}/test_1.txt', sep='\t', decimal=',', encoding=encoding, header=None, names=header)
    
    if table_styling in tabulate_formats:
        write_stats(df, 'test_1_stats.txt', encoding=encoding, table_styling=table_styling)
    else:
        write_stats(df, 'test_1_stats.txt', encoding=encoding)
 
    saving_time = get_mean_saving_time(df)
    print(saving_time)
            
    

if __name__ == '__main__':
    table_styling = None
    if len(sys.argv) > 1:
        table_styling = sys.argv[1]
        
    main(table_styling)
    
    