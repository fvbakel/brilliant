#
# Convert the Primes json output to csv

import json
import os

class prime_parser:
    header = ['implementation', 'solution', 'label', 'passes', 'duration', 'threads', 'tag: algorithm', 'tag: faithful', 'tag: bits']

    def write_header():
        print(",".join(prime_parser.header))

    def process_json(file_name):
        # Opening JSON file
        f = open(file_name)
        
        # returns JSON object as 
        # a dictionary
        data = json.load(f)
        
        # Iterating through the json
        # list
        for result in data['results']:
            # write fields
            row = []
            for field in prime_parser.header:
                if field.startswith('tag: '):
                    field = field.replace('tag: ','')
                    if 'tags' in result and field in result['tags']:
                        row.append(str(result['tags'][field]))
                    else:
                        row.append("")
                else:
                    if field in result:
                        row.append(str(result[field]))
                    else:
                        row.append("")
            
            print(",".join(row))
    
    def process_dir(dir_name):
        prime_parser.write_header()
        directory = os.fsencode(dir_name)
            
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".json"): 
                fullname = os.path.join(dir_name, filename)
                prime_parser.process_json(fullname)

prime_parser.process_dir('./data')

