from dataclasses import dataclass
from argparse import ArgumentParser

import json
import wikipagelinks as pl


def loadParameters(configFilename):
    with open(configFilename, 'r') as f:
        config = json.load(f)

    return config

def writeSampleConfig():
    param = dict()
    param['db_file']         = 'pagelinks.db'
    param['max_depth']       = 3
    param['source_url']      = 'https://nl.wikipedia.org/?curid='
    param['graph_dir']       = 'graphs'
    
    #write it back to the file
    with open('example_config.json', 'w') as f:
        json.dump(param, fp=f, indent=4)

def main():
    parser = ArgumentParser(description="Find a path between two wiki pages, based on sqlite database\n")
    required = parser.add_argument_group('Required arguments')
    required.add_argument("--start", "-s", help="Start the search from this page", type=str, required=False, default=None)
    required.add_argument("--end", "-e", help="The page to find", type=str, required=False, default=None)

    parser.add_argument("--file", "-f", help="Filename of the config file, find_config.json if not specified", type=str, required=False, default='find_config.json')
    parser.add_argument("--config", "-c", help="Write an example config file named example_config.json",action='store_true')
    args = parser.parse_args()

    if args.config:
        writeSampleConfig()
#    elif args.help is not None:
#        parser.print_help()
    else:
        param=loadParameters(args.file)

        db = pl.PagesDb(db_file=param['db_file'],source_url=param['source_url'] )
        finder = pl.PagePathFinder(pagesDb=db,start_title=args.start,end_title=args.end)
        finder.find(max_depth=param['max_depth'])

        if finder.pathsfound > 0:
            finder.writeGraph(directory=param['graph_dir'])

        
if __name__ == '__main__':  
    main()