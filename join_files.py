import os
import pprint
from chardet import detect
import pandas as pd
from tabulate import tabulate, tabulate_formats
import sys
import numpy as np
from datetime import datetime
from csv import QUOTE_MINIMAL

MEASUREMENTS_PATH = 'measurements/test_240202'
MEASUREMENTS_STATS_PATH = 'files_statistics'
N_OF_FILES = 14
SAMPLES_PER_LOOP = 16520 # The NI9234 takes 16520 samples than stop to save them in a .txt file

printer = pprint.PrettyPrinter()
pp = printer.pprint


def get_file_encoding(file_name: str) -> str:
    file_path = f'{MEASUREMENTS_PATH}/{file_name}'
    
    with open(file_path, 'rb') as file:
        result = detect(file.read())
       
    encoding = result['encoding'] if result['encoding'] != 'ascii' else 'utf-8' #returns utf-8 if encoding in ASCII
       
    print(f"The file's encoding is [{encoding}] with {result['confidence']*100}% confidence.") 
    return encoding

def write_stats(df: pd.DataFrame, file_name: str, encoding='utf-8', table_styling='rounded_outline') -> int:
    if not os.path.exists(MEASUREMENTS_STATS_PATH):
        os.makedirs(MEASUREMENTS_STATS_PATH)
        
    file_stats = df.describe()
    count = int(file_stats.iloc[0, 1])
    file_stats.drop('count', inplace=True)
    
    file_path = f'{MEASUREMENTS_STATS_PATH}/{file_name}'
    table = tabulate(file_stats, headers='keys', tablefmt=table_styling, floatfmt=".7f")
    with open(file_path, 'w', encoding=encoding) as file:
        file.write(table)
        file.write(f'\n\nNumber of measuments = {count}')
    
    return count

def get_mean_saving_time(df: pd.DataFrame, LOOPS_PER_FILE: str) -> float:
    saving_time = 0    
    for i in range(1, LOOPS_PER_FILE):
        saving_time+= df.at[SAMPLES_PER_LOOP*i, 'time'] - df.at[SAMPLES_PER_LOOP*i-1, 'time']
    saving_time = saving_time / (LOOPS_PER_FILE-1)
    
    return saving_time.round(6)

def get_df_list(encoding) -> dict[str, list[pd.DataFrame | int]]:
    files = [file for _, _, files in os.walk(MEASUREMENTS_PATH) for file in files]
    files.sort(key=lambda item: int(item.split('_')[1].split('.')[0]))
    
    header = ['time', 'x', 'y', 'z']
    files_dict = {}
    for file in files:
        files_dict[file] = [pd.read_csv(f'{MEASUREMENTS_PATH}/{file}', sep='\t', decimal=',', encoding=encoding, header=None, names=header)]

    return files_dict

def main(table_styling):
    encoding = get_file_encoding('test_1.txt')
    
    files_dict = get_df_list(encoding)

    saving_time = 0
    for key, value in files_dict.items():
        df = value[0]
        stat_file_name = key.replace('.txt', '_stats.txt')
        if table_styling in tabulate_formats:
            n_of_readings = write_stats(df, stat_file_name, encoding=encoding, table_styling=table_styling)
        else:
            n_of_readings = write_stats(df, stat_file_name, encoding=encoding)
        files_dict[key].append(n_of_readings)
        
        loops_per_reading = int(n_of_readings/SAMPLES_PER_LOOP)
        saving_time += get_mean_saving_time(df, loops_per_reading)
            
    avrg_saving_time = saving_time/N_OF_FILES
    print(f'{avrg_saving_time=}')
    
    updated_dfs = [files_dict['test_1.txt'][0]]
    last_value: float = files_dict['test_1.txt'][0]['time'].iat[-1]
    for file, content in files_dict.items():
        if file == 'test_1.txt':
            continue
        df = content[0]
        n_of_samples = content[1]
        discrete_diff = df['time'].diff()
        df['time'].iat[0] = (last_value + avrg_saving_time).round(6)
        s = df['time']
        for i in range(1, n_of_samples):
            s.iat[i] = s.iat[i-1] + discrete_diff.iat[i]
        last_value = df['time'].iat[-1]
        updated_dfs.append(df)    
        
    joined: pd.DataFrame = pd.concat(updated_dfs, ignore_index=True)
    joined.to_csv('measurements/joined_file.tsv', sep='\t', encoding=encoding, quoting=QUOTE_MINIMAL, float_format='%.6f', decimal=',', index=False)
    
    

if __name__ == '__main__':
        
    table_styling = None
    if len(sys.argv) > 1:
        table_styling = sys.argv[1]
        
    main(table_styling)
    
    