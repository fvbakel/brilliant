from dataclasses import dataclass
from argparse import ArgumentParser
from re import sub
from tabnanny import filename_only
from typing import Dict

import sqlite3
import time

import graphviz

from enum import Enum

class ExtendedEnum(Enum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class RelationDirection(ExtendedEnum):
    DIR_TO   = 'to'
    DIR_FROM_= 'from'

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

class Page:

    def __init__(self,page_id:int,title:str = ''):
        self.page_id    = page_id
        self.title      = title
        self.children:set['Page'] = None
        self.parents: set['Page'] = None

    def __hash__(self):
        return self.page_id

    def addChild(self,childPage:'Page'):
        if self.page_id == childPage.page_id:
            return

        if self.children is None:
            self.children = set()
        self.children.add(childPage)
        childPage._addParent(self)
    
    def _addParent(self,parentPage:'Page'):
        if self.page_id == parentPage.page_id:
            return

        if self.parents is None:
            self.parents = set()
        self.parents.add(parentPage)
    
    def hasChildren(self) -> bool:
        return self.children != None
    
    def hasParents(self) -> bool:
        return self.parents != None
    
class PagesDb:
    def __init__(self, db_file:str):
        self.db_file                    = db_file
        self._conn                      = None
        self._eventLog                  = EventLog()

        self._open_db()
        self.source_url                 = self._getSourceUrl()
    
    def _getSourceUrl(self):
        cursor = self._conn.cursor()
        sql = """   
            SELECT value
            FROM meta
            where 
                field = 'source_url'
        """
        cursor.execute(sql,)
        rows = cursor.fetchall()

        nr_found = len(rows)
        if  nr_found == 1:
            return rows[0][0]
        elif nr_found == 0:
            self._eventLog.report('ERROR','source_url not found in meta table')
            return None
        else:
            self._eventLog.report('ERROR','source_url found multiple times in meta table: {}'.format(nr_found))
            return None

    def getUrl(self,page_id:int) -> str:
        return self.source_url + str(page_id)

    def findPaths(self, start_id:int,end_id:int,max_level:int,max_nr_of_paths:int):
        event = 'Search paths to [{}] start at [{}] max search dept [{}]'.format(
            end_id,
            start_id,
            max_level
        )
        self._eventLog.startEvent(event)
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
            LIMIT ?
            ;
        """
        #cursor.row_factory = lambda cursor, row: row[0]
        cursor.execute(sql,[start_id,end_id,max_level,max_nr_of_paths])
        self._eventLog.endEvent(event)
        return cursor.fetchall()
            
    def getChildren(self,page_id:int):
        cursor = self._conn.cursor()
        sql = """   
            SELECT 
                p.page_id
            FROM pagelinks l
            join pages p on p.page_id = l.pl_to
            where 
                pl_from = ?
        """
        #cursor.row_factory = lambda cursor, row: {'foo': row[0]}
        cursor.execute(sql,[page_id])
        return cursor

    def getParents(self,page_id:int):
        cursor = self._conn.cursor()
        sql = """   
            SELECT 
                p.page_id
            FROM pagelinks l
            join pages p on p.page_id = l.pl_from
            where 
                pl_to = ?
        """
        #cursor.row_factory = lambda cursor, row: {'foo': row[0]}
        cursor.execute(sql,[page_id])
        return cursor

    def getPageId4Title(self,title:str):
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
            self._eventLog.report('ERROR','Title not found: {}'.format(title))
            return None
        else:
            self._eventLog.report('ERROR','Title found multiple times: {}'.format(nr_found))
            return None

    def getTitle4PageId(self,page_id:int):
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

    def top(self,direction:RelationDirection,number:int):
        cursor = self._conn.cursor()
        sql = """   
            SELECT
                p.page_id,
                p.title,
                top.nr
            FROM (
                SELECT 
                    l.pl_to as page_id,
                    count(l.pl_from) as nr
                FROM pagelinks l
                GROUP BY l.pl_to
                ORDER BY count(l.pl_to) DESC
                LIMIT ?
            ) top
            JOIN pages p ON p.page_id = top.page_id
        """
        if direction == 'from':
            sql = sql.replace('pl_from','pl_tmp')
            sql = sql.replace('pl_to','pl_from')
            sql = sql.replace('pl_tmp','pl_to')
        cursor.execute(sql,[number])
        return cursor.fetchall()

    def _open_db(self):
        event = 'Open database'
        self._eventLog.startEvent(event)
        self._conn = sqlite3.connect(self.db_file)
        self._eventLog.endEvent(event)

    def __del__(self):
        event = 'Close database'
        self._eventLog.startEvent(event)
        if self._conn:
            self._conn.close()
        self._eventLog.endEvent(event)

class PageHandler:
    def __init__(self,pagesDb:PagesDb):
        self.pagesDb    = pagesDb
        self._eventLog  = EventLog()
        self.clear()
    
    def clear(self):
        self.pages:Dict[int, Page]    = dict()

    def getPage(self,page_id:int,loadTile = True) -> Page:
        if isinstance(page_id,str):
            page_id = int(page_id)
        
        if not isinstance(page_id,int):
            self._eventLog.report("ERROR"," invalid page_id [{}] type is [{}]".format(page_id,type(page_id)))
            return

        if page_id not in self.pages:
            title = ''
            if loadTile:
                title = self.pagesDb.getTitle4PageId(page_id)
            result_page = Page(page_id,title)
            self.pages[page_id] = result_page
        return self.pages[page_id]
    
    def loadTitle(self,page:Page):
        page.title = self.pagesDb.getTitle4PageId(page.page_id)

    def getPage4Title(self,title:str) -> Page:
        page_id = self.pagesDb.getPageId4Title(title)
        if isinstance(page_id,int):
            if page_id not in self.pages:
                result_page = Page(page_id,title)
                self.pages[page_id] = result_page
            return self.pages[page_id]
        else:
            return None
    
    def findPaths(self,start:Page,end:Page,max_depth:int,max_nr_of_paths = 100) -> int:
        paths = self.pagesDb.findPaths(
            start_id=start.page_id,
            end_id=end.page_id,
            max_level = max_depth,
            max_nr_of_paths=max_nr_of_paths
        )

        nrOfPaths = 0
        if paths != None:
            nrOfPaths = len(paths)
        self._eventLog.report('INFO','Nr of paths found: [{}]'.format(nrOfPaths))

        if paths != None:
            for path in paths:
                page_ids = path[1].split('-')
                tailPage = self.getPage(page_ids[0])
                for page_id in page_ids[1:]:
                    childPage = self.getPage(page_id)
                    tailPage.addChild(childPage)
                    tailPage = childPage
        
        return nrOfPaths

    def loadChildren(self,parent:Page):
        event = f'Load child relations for {parent.page_id}'
        self._eventLog.startEvent(event)
        cursor      = self.pagesDb.getChildren(parent.page_id)
        chunk_size  = 10000
        chunk       = cursor.fetchmany(chunk_size)
        while len(chunk) > 0:
            for row in chunk:
                parent.addChild(self.getPage(row[0]))
            chunk = cursor.fetchmany(chunk_size)
        self._eventLog.endEvent(event)
    
    def loadParents(self,child:Page):
        event = f'Load parent relations for {child.page_id}'
        self._eventLog.startEvent(event)
        cursor      = self.pagesDb.getParents(child.page_id)
        chunk_size  = 10000
        chunk       = cursor.fetchmany(chunk_size)
        while len(chunk) > 0:
            for row in chunk:
                parent = self.getPage(row[0])
                parent.addChild(child)
            chunk = cursor.fetchmany(chunk_size)
        self._eventLog.endEvent(event)

class PagePathFinder:
    def __init__(self,pagesDb:PagesDb,start_title:str,end_title:str):
        self.pagesDb        = pagesDb
        self.pageHandler    = PageHandler(self.pagesDb)
        self.pathsfound     = None

        self._eventLog      = EventLog()

        self.startPage      = self.pageHandler.getPage4Title(start_title)
        self.endPage        = self.pageHandler.getPage4Title(end_title)
        
        if self.startPage is None:
            msg = 'Can not find page: [{}]'.format(start_title)
            raise ValueError(msg)
        
        if self.endPage is None:
            msg = 'Can not find page: [{}]'.format(end_title)
            raise ValueError(msg)

    def find(self,max_depth:int,max_nr_of_paths = 100):
        if self.pathsfound is None:
            self.pathsfound = self.pageHandler.findPaths(self.startPage,self.endPage,max_depth,max_nr_of_paths)
        return self.pathsfound
    
    def clear(self):
        self.pageHandler.clear()
        self.startPage  = self.pageHandler.getPage(self.startPage.page_id)
        self.endPage    = self.pageHandler.getPage(self.endPage.page_id)
        self.pathsfound = None

    def writeGraph(self,directory:str):
        graph = Pages2Graph(self.pageHandler)
        graph.makePlainGraph()
        filename = str(self.startPage.page_id) + '-' + str(self.endPage.page_id)
        graph.render(filename=filename,directory=directory, format='svg')
        return filename
    
    def dumpPaths(self):
        self._printPath(self.startPage,[self.startPage.title])
    
    def _printPath(self,page:Page,path:list):
        if page.hasChildren():
           for child in page.children:
               if child.title not in set(path):
                self._printPath(child,path + [child.title])
        else:
            print(path)

class PageTopFinder:
    def __init__(self,pagesDb:PagesDb):
        self.pagesDb        = pagesDb
        self._results       = None

    def find(self,direction:RelationDirection,number:int):
        self._results = self.pagesDb.top(direction=direction,number=number)

    def dumpResults(self):
        if self._results != None:
            width = len(str(self._results[0][2]))
            for result in self._results:
                print(f"{ result[2]:{' '}{'>'}{width}} : {result[1]}")


class Pages2Graph:

    def __init__(self,pageHandler:PageHandler):
        self._pageHandler = pageHandler
        self.reset()        
 
    def reset(self):
        self._sub_graphs: dict[str, graphviz.Digraph] = dict()
        self.dot = graphviz.Digraph()
        self.maincluster:set[Page] = set()

    def makePlainGraph(self):
        self.dot.attr(rankdir='LR')
        for page_id,page in self._pageHandler.pages.items():
            self.dot.node(name=str(page_id),label=page.title,URL=self._pageHandler.pagesDb.getUrl(page_id))
        
        self._addChildRelations()

    def makeSimpleClusterGraph(self):
        self.dot.attr(rankdir='LR')
        self._addSimpleClusters()
        self._addChildRelations()
    
    def _addNode(self,graph:graphviz.Digraph,page:Page):
        graph.node(name=str(page.page_id),label=page.title,URL=self._pageHandler.pagesDb.getUrl(page.page_id))

    def _makeSubGraph(self,name:str):
        self._sub_graphs[name] = graphviz.Digraph(name=name)
        self._sub_graphs[name].attr(rankdir='LR',color='lightgrey')

    def _addSimpleClusters(self):
        self._makeSubGraph(name='cluster_children_only')
        self._makeSubGraph(name='cluster_parents_only')
        self._makeSubGraph(name='cluster_both')
        self._makeSubGraph(name='cluster_no_relations')
        self._makeSubGraph(name='cluster_main')

        for page_id,page in self._pageHandler.pages.items():
            
            if page in self.maincluster:
                sub_graph = 'cluster_main'
            elif page.hasChildren() and page.hasParents():
                sub_graph = 'cluster_both'
            elif page.hasChildren():
                sub_graph = 'cluster_children_only'
            elif page.hasParents():
                sub_graph = 'cluster_parents_only'
            else:
                sub_graph = 'cluster_no_relations'
            #self._sub_graphs[sub_graph].node(name=str(page_id),label=page.title,URL=self._pageHandler.pagesDb.getUrl(page_id))
            self._addNode(self._sub_graphs[sub_graph],page)
        
        for name,graph in self._sub_graphs.items():
            self.dot.subgraph(graph)
        

    def _addChildRelations(self):
        for page_id,page in self._pageHandler.pages.items():
            if page.hasChildren():
                for child in page.children:
                    self.dot.edge(str(page_id),str(child.page_id))

    def render(self,filename:str,directory:str, format='svg'):
        self.dot.render(filename=filename,directory=directory, format=format)

#
# Main functions

def findPaths(
        db_file:str,
        start_title:str,
        end_title:str,
        graph_dir:str,
        max_depth=3,
        max_nr_of_paths=100
    ):
        db = PagesDb(db_file=db_file)
        finder = PagePathFinder(pagesDb=db,start_title=start_title,end_title=end_title)
        finder.find(max_depth=max_depth,max_nr_of_paths=max_nr_of_paths)

        if finder.pathsfound > 0:
            finder.dumpPaths()
            finder.writeGraph(directory=graph_dir)

def top(db_file:str,direction:RelationDirection,number:int):
    db  = PagesDb(db_file=db_file)
    top = PageTopFinder(pagesDb=db)
    top.find(direction=direction,number=number)

    top.dumpResults()

def clusters(db_file:str):
    db  = PagesDb(db_file=db_file)
    print('Sorry not implemented')

def graph(db_file:str,title:str,directory:str):
    db  = PagesDb(db_file=db_file)
    ph = PageHandler(db)
    basePage = ph.getPage4Title(title)
    if basePage is None:
        msg = f'Can not find page: [{title}]'
        raise ValueError(msg)
    ph.loadChildren(basePage)
    ph.loadParents(basePage)
    graph = Pages2Graph(ph)
    graph.maincluster.add(basePage)
    graph.makeSimpleClusterGraph()
    filename = str(basePage.page_id)
    graph.render(filename=filename,directory=directory)