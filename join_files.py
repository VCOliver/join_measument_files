import os
import pprint

MEASUREMENTS_PATH = 'measurements/test_240202'

printer = pprint.PrettyPrinter()
pp = printer.pprint

if __name__ == '__main__':
    files = os.listdir(MEASUREMENTS_PATH)
    for file in files:
        new_name = file.replace('t.', 't_')
        old_path = os.path.join(MEASUREMENTS_PATH, file)
        new_path = os.path.join(MEASUREMENTS_PATH, new_name)
        
        # Rename the file
        os.rename(old_path, new_path)