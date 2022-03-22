from dataclasses import dataclass
from argparse import ArgumentParser

import sqlite3
import time
import json

@dataclass
class ParametersFindWikiPath:
    db_file:     str
    max_depth:   int


class EventLog:

    def __init__(self):
        self.start_time = None
        self.last_time  = None

    def report(self,level:str,msg: str):
        print('{}: {}'.format(level,msg))
    
    def startEvent(self,event:str):
        msg = 'Start {}'.format(event)
        self.last_time = time.perf_counter()
        self.report('INFO',msg)
    
    def endEvent(self,event:str):
        now = time.perf_counter()
        duration = now - self.last_time
        msg = '{} took {:.2f} seconds'.format(event,duration)
        self.report('INFO',msg)

class FindWikiPath:

    def __init__(self, parameters: ParametersFindWikiPath):
        self.parameters = parameters
        self.conn = None
        self.eventLog = EventLog()
        self._open_db()
   
    def find(self,start: str,end: str):
        event = 'Search [{}] start at [{}] max search dept [{}]'.format(
            end,
            start,
            self.parameters.max_depth
        )
        self.eventLog.startEvent(event)

        start_page_id = self._getPageId4Title(start)
        end_page_id = self._getPageId4Title(start)

        if start_page_id != None and end_page_id != None:        
            paths = self._find(start_page_id,end_page_id, self.parameters.max_depth)
            if paths != None and len(paths) > 0:
                print('Path found')
                print(paths)
            else:
                print('No path not found')

        self.eventLog.endEvent(event)
    
    def _find(self, start_id:int,end_id:int,max_level:int):
        cursor = self.conn.cursor()
        sql = """   
            WITH RECURSIVE
                parameters(start_id,end_id,max_level) as (
                    select 
                        ?,
                        ?,
                        ?
                ),
                sub_rels(child,level,path) AS (
                    SELECT 
                        start_id,
                        0,
                        '' || start_id
                        from parameters
                        where 
                                start_id is not null
                            and end_id is not null
                    UNION ALL
                    SELECT 
                        rels.pl_from,
                        sub_rels.level + 1,
                        sub_rels.path || '-' || rels.pl_to
                    FROM pagelinks rels, sub_rels
                    WHERE 
                            rels.pl_from = sub_rels.child
                        and sub_rels.level < (select max_level from parameters)
                )
            SELECT sub_rels.path 
            FROM sub_rels,parameters
            WHERE   sub_rels.child = parameters.end_id
            ;
        """
        #cursor.row_factory = lambda cursor, row: {'foo': row[0]}
        cursor.execute(sql,[start_id,end_id,max_level])
        return cursor.fetchall()

    def _getChilds(self,page_id:int):
        cursor = self.conn.cursor()
        sql = """   
            SELECT 
                p.page_id,
                p.title
            FROM pagelinks l
            join pages p on p.title = replace(l.pl_title,'_',' ')
            where 
                pl_from = ?
        """
        #cursor.row_factory = lambda cursor, row: {'foo': row[0]}
        cursor.execute(sql,[page_id])
        return cursor.fetchall()

    def _getPageId4Title(self,title:str):
        cursor = self.conn.cursor()
        sql = """   
            SELECT page_id
            FROM pages
            where 
                title = ?
        """
        cursor.execute(sql,[title])
        rows = cursor.fetchall()
        nr_found = len(rows)

        if  nr_found == 1:
            return rows[0][0]
        elif nr_found == 0:
            self.eventLog.report('ERROR','Title not found: {}'.format(title))
            return None
        else:
            self.eventLog.report('ERROR','Title found multiple times: {}'.format(nr_found))
            return None


    def _open_db(self):
        event = 'Open database'
        self.eventLog.startEvent(event)
        self.conn = sqlite3.connect(self.parameters.db_file)
        self.eventLog.endEvent(event)

    def __del__(self):
        event = 'Close database'
        self.eventLog.startEvent(event)
        if self.conn:
            self.conn.close()
        self.eventLog.endEvent(event)


def loadParameters(configFilename):
    with open(configFilename, 'r') as f:
        config = json.load(f)

    return ParametersFindWikiPath(config['db_file'], config['max_depth'])

def writeSampleConfig():
    param = ParametersFindWikiPath(
        db_file     = 'pagelinks.db',
        max_depth       = 3
    )

    #write it back to the file
    with open('example_config.json', 'w') as f:
        json.dump(param.__dict__, fp=f, indent=4)

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
        parameters=loadParameters(args.file)
        finder = FindWikiPath(parameters)
        finder.find(args.start,args.end)

if __name__ == '__main__':  
    main()