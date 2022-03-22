from dataclasses import dataclass
from argparse import ArgumentParser
from typing import Dict

import sqlite3
import time
import json

import graphviz

@dataclass
class ParametersFindWikiPath:
    db_file:     str
    max_depth:   int

@dataclass
class Page:
    page_id:     int
    title:       str
    page_links:  set('Page') = None

    def __hash__(self):
        return self.page_id.__hash__()

    def addLink(self,childPage:'Page'):
        if self.page_links is None:
            self.page_links = set()
        self.page_links.add(childPage)
    
    def hasLinks(self) -> bool:
        return self.page_links != None

    def getUrl(self) -> str:
        return 'https://nl.wikipedia.org/?curid=' + str(self.page_id)

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
        self._parameters                = parameters
        self._conn                      = None
        self._pages: Dict[int, Page]    = dict()
        self._startpage:Page            = None
        self._endpage:Page              = None
        self._eventLog                  = EventLog()

        self._open_db()
   
    def find(self,start: str,end: str):
        event = 'Search [{}] start at [{}] max search dept [{}]'.format(
            end,
            start,
            self._parameters.max_depth
        )
        self._eventLog.startEvent(event)

        start_page_id = self._getPageId4Title(start)
        end_page_id   = self._getPageId4Title(end)
        
        if start_page_id != None and end_page_id != None:
            self._startpage = self._getPage(start_page_id)
            self._endpage = self._getPage(end_page_id)
            paths = self._find(self._parameters.max_depth)
            if paths != None and len(paths) > 0:
                print('Nr of path found: [{}]'.format(len(paths)))
                self._makePages(paths)
                self._printPaths()
                self._makeGraph()
            else:
                print('No path not found')
        else:
            if start_page_id is None:
                self._eventLog.report('ERROR:','Can not find page: [{}]'.format(start))
            if start_page_id is None:
                self._eventLog.report('ERROR:','Can not find page: [{}]'.format(end))

        self._eventLog.endEvent(event)
    
    def _find(self, max_level:int):
        cursor = self._conn.cursor()
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
                        rels.pl_to,
                        sub_rels.level + 1,
                        sub_rels.path || '-' || rels.pl_to
                    FROM pagelinks rels, sub_rels
                    WHERE 
                            rels.pl_from = sub_rels.child
                        and sub_rels.level < (select max_level from parameters)
                        and sub_rels.child != (select end_id from parameters)
                )
            SELECT sub_rels.level,sub_rels.path
            FROM sub_rels,parameters
            WHERE   
                    sub_rels.child = parameters.end_id
            --ORDER BY sub_rels.level ASC
            LIMIT 100
            ;
        """
        #cursor.row_factory = lambda cursor, row: row[0]
        cursor.execute(sql,[self._startpage.page_id,self._endpage.page_id,max_level])
        return cursor.fetchall()

    def _printPaths(self):
       self._printPath(self._startpage,self._startpage.title)
    
    def _printPath(self,page:Page,path:str):
        if page.hasLinks():
           for child in page.page_links:
               self._printPath(child,path + '->' + child.title)
        else:
            print(path)

    def _getTilePaths(self,paths:list):
        title_paths = []
        for path in paths:
            page_ids = path[1].split('-')
            title_path = []
            for page_id in page_ids:
                title_path.append(self._getTitle4PageId(page_id))
            title_paths.append(title_path)
        return title_paths
    
    def _getPage(self,page_id:int) -> Page:
        if (isinstance(page_id,str)):
            page_id = int(page_id)
        
        if (isinstance(page_id,int)):
            if page_id not in self._pages:
                result_page = Page(page_id,self._getTitle4PageId(page_id))
                self._pages[page_id] = result_page
            return self._pages[page_id]
        else:
            self._eventLog.report("ERROR"," invalid page_id [{}] type is [{}]".format(page_id,type(page_id)))

    def _makePages(self,paths:list):
        for path in paths:
            page_ids = path[1].split('-')
            tailPage = self._getPage(page_ids[0])
            for page_id in page_ids[1:]:
                childPage = self._getPage(page_id)
                tailPage.addLink(childPage)
                tailPage = childPage

    def _makeGraph(self):
        dot = graphviz.Digraph()
        dot.attr(rankdir='LR')
        for page_id,page in self._pages.items():
            dot.node(name=str(page_id),label=page.title,URL=page.getUrl())
            if page.hasLinks():
                for child in page.page_links:
                    dot.edge(str(page_id),str(child.page_id))
        dot.render('graphs/' + str(self._startpage.page_id) + '-' + str(self._endpage.page_id) + '.gv', format='svg')

            
    def _getChilds(self,page_id:int):
        cursor = self._conn.cursor()
        sql = """   
            SELECT 
                p.page_id,
                p.title
            FROM pagelinks l
            join pages p on p.page_id = l.pl_to
            where 
                pl_from = ?
        """
        #cursor.row_factory = lambda cursor, row: {'foo': row[0]}
        cursor.execute(sql,[page_id])
        return cursor.fetchall()

    def _getPageId4Title(self,title:str):
        cursor = self._conn.cursor()
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

    def _getTitle4PageId(self,page_id:int):
        cursor = self._conn.cursor()
        sql = """   
            SELECT title
            FROM pages
            where 
                page_id = ?
        """
        cursor.execute(sql,[page_id])
        rows = cursor.fetchall()
        nr_found = len(rows)

        if  nr_found == 1:
            return str(rows[0][0])
        elif nr_found == 0:
            self._eventLog.report('ERROR','Page id not found: {}'.format(page_id))
            return None
        else:
            self._eventLog.report('ERROR','Page id found multiple times: {}'.format(nr_found))
            return None


    def _open_db(self):
        event = 'Open database'
        self._eventLog.startEvent(event)
        self._conn = sqlite3.connect(self._parameters.db_file)
        self._eventLog.endEvent(event)

    def __del__(self):
        event = 'Close database'
        self._eventLog.startEvent(event)
        if self._conn:
            self._conn.close()
        self._eventLog.endEvent(event)


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