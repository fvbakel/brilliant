from dataclasses import dataclass
from argparse import ArgumentParser

import json
import pagelinks as pl


class FindPageCommand:
    def __init__(self):
        self._parser = ArgumentParser(description=
            """Different ways to search through wiki page relations. The searches are based on a sqlite database
            that was created with wikiPagelinks2sqlite.py.
            """
        )
        self._parser.set_defaults(func=self._no_args)
        self._parser.add_argument("-f","--file", help="Filename of the config file, find_config.json if not specified", type=str, required=False, default='find_config.json')

        sub_parsers = self._parser.add_subparsers()
        parser_1 = sub_parsers.add_parser('path',help='Find a path between two wiki pages')
        parser_1.add_argument("start", help="Start the search from this page",type=str, default=None)
        parser_1.add_argument("end", help="The page to find", type=str, default=None)
        parser_1.set_defaults(func=self._path)

        parser_2 = sub_parsers.add_parser('top',help="Make a list of the top pages ranked by number of links")
        parser_2.add_argument("-d","--direction", choices=pl.RelationDirection.list(),help="Rank by the most links to or from this page, default to", type=str, required=False, default='to')
        parser_2.add_argument("-n","--number", help="Number of links to report, default 10", type=int, required=False, default=10)
        parser_2.set_defaults(func=self._top)

        parser_3 = sub_parsers.add_parser('clusters',help="Make separate clusters of pages")
        parser_3.set_defaults(func=self._clusters)

        parser_4 = sub_parsers.add_parser('graph',help="Make a graph of the page")
        parser_4.add_argument("title", help="The title of the page to use as the top of the graph", type=str, default=None)
        parser_4.set_defaults(func=self._graph)

        parser_99 = sub_parsers.add_parser('config',help="Write an example config file named example_config.json")
        parser_99.set_defaults(func=self._config)
         
        self._args = self._parser.parse_args()

    def run(self):
        self._args.func()

    def _top(self):
        param=self._loadParameters(self._args.file)

        pl.top(
            db_file   = param['db_file'],
            direction = self._args.direction,
            number    = self._args.number
        )

    def _path(self):
        param=self._loadParameters(self._args.file)
        pl.findPaths(
            db_file = param['db_file'],
            start_title=self._args.start,
            end_title=self._args.end,
            graph_dir=param['graph_dir'],
            max_depth=param['max_depth'],
            max_nr_of_paths=param['max_nr_of_paths'],
            source_url=param['source_url']
        )

    def _clusters(self):
        param=self._loadParameters(self._args.file)
        pl.clusters(db_file = param['db_file'])
    
    def _graph(self):
        param=self._loadParameters(self._args.file)
        pl.graph(
            db_file = param['db_file'],
            title=self._args.title,
            directory=param['graph_dir']
        )

    def _config(self):
        param = dict()
        param['db_file']         = 'pagelinks.db'
        param['max_depth']       = 3
        param['max_nr_of_paths'] = 100
        param['source_url']      = 'https://nl.wikipedia.org/?curid='
        param['graph_dir']       = 'graphs'
        
        #write it back to the file
        with open('example_config.json', 'w') as f:
            json.dump(param, fp=f, indent=4)
    
    def _no_args(self):
        self._parser.print_help()
    
    def _loadParameters(self,configFilename):
        with open(configFilename, 'r') as f:
            config = json.load(f)

        return config

def main():
    
    command = FindPageCommand()
    command.run()
        
if __name__ == '__main__':  
    main()