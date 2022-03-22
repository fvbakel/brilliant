from dataclasses import dataclass
from pathlib import Path
from argparse import ArgumentParser

import os
import sqlite3
import time
import json

@dataclass
class ParametersWiki2Sqlite:
    input_file:      str
    input_page_file: str
    output_file:     str
    error_file:      str

class Wiki2Sqlite:

    def __init__(self, parameters: ParametersWiki2Sqlite):
        self.parameters = parameters
        #self.out_file = None
        self.conn = None
        self.start_time = None
        self.last_time  = None

    def convert(self):
        self.start_time = time.perf_counter()
        self.last_time = self.start_time
        self._openOutput()
        self._createImportTables()
        self._importPagelinks()
        self._importPages()
        self._postImport()
        self._closeOutput()
    
    def _report(self,level:str,msg: str):
        print('{}: {}'.format(level,msg))
    
    def _startEvent(self,event:str):
        msg = 'Start {}'.format(event)
        self.last_time = time.perf_counter()
        self._report('INFO',msg)
    
    def _endEvent(self,event:str):
        now = time.perf_counter()
        duration = now - self.last_time
        msg = '{} took {:.2f} seconds'.format(event,duration)
        self._report('INFO',msg)

    def _importPagelinks(self):
        self._startEvent('Pagelink import')
        count = 0
        with open(self.parameters.input_file, 'r',encoding='utf-8',errors='replace') as in_file:
            for line in in_file:
                count += 1
                if line.startswith('INSERT INTO '):
                    self._parseLinkLine(count,line)
        self._endEvent('Pagelink import')

    def _createImportTables(self):
        self._startEvent('Create import tables')
        sql = """
            CREATE TABLE pages (
                `page_id` int(11) DEFAULT 0,
                `title` varbinary(255) NOT NULL DEFAULT ''
            );
        """
        self.conn.execute(sql)

        sql = """
            CREATE TABLE `pagelinks` (
                `pl_from` int(8) NOT NULL DEFAULT 0,
                `pl_namespace` int(11) NOT NULL DEFAULT 0,
                `pl_title` varbinary(255) NOT NULL DEFAULT '',
                `pl_from_namespace` int(11) NOT NULL DEFAULT 0
            );
        """
        self.conn.execute(sql)
        self._endEvent('Create import tables')
    
    def _postImport(self):
        self._startEvent('Post process: create a temp index')
        sql = """
            create index i_pagelinks_tmp 
                on pagelinks(pl_title)
            ;
        """
        self.conn.execute(sql)
        self._endEvent('Post process: create a temp index')
        
        self._startEvent('Post process: create pages index')
        sql = """
            create index i_pages 
                on pages (page_id)
            ;
        """
        self.conn.execute(sql)
        self._endEvent('Post process: create pages index')

        event_name = 'Post process: create pages title index'
        self._startEvent(event_name)
        sql = """
            create index i_pages_title
                on pages (title)
            ;
        """
        self.conn.execute(sql)
        self._endEvent(event_name)

        self._startEvent('Post process: create new table')
        sql = """
            create table pagelinks_clean as
                SELECT 
                    l.pl_from       as pl_from,
                    p_to.page_id    as pl_to
                    FROM pagelinks l
                    join pages p_from on p_from.page_id = l.pl_from
                    join pages p_to on p_to.title = replace(l.pl_title,'_',' ')
            ;
        """
        self.conn.execute(sql)
        self._endEvent('Post process: create new table')

        self._startEvent('Post process: dropping temp table')
        sql = """
            drop table pagelinks;
        """
        self.conn.execute(sql)
        self._endEvent('Post process: dropping temp table')

        self._startEvent('Post process: rename pagelinks table')
        sql = """
            alter table pagelinks_clean rename to pagelinks;
        """
        self.conn.execute(sql)
        self._endEvent('Post process: rename pagelinks table')

        self._startEvent('Post process: create pagelinks index')
        sql = """
            create index i_pagelinks_from
                on pagelinks(pl_from,pl_to)
            ;
        """
        self.conn.execute(sql)
        self._endEvent('Post process: create pagelinks index')

        self._startEvent('Post process: resize (vacuum) database file')
        sql = """
            vacuum;
        """
        self.conn.execute(sql)
        self._endEvent('Post process: resize (vacuum) database file')

    def _openOutput(self):
        #self.out_file = open(self.parameters.output_file,'w')
        db_file = Path(self.parameters.output_file)
        if db_file.exists():
            os.remove(self.parameters.output_file)
        self.conn = sqlite3.connect(self.parameters.output_file)
        self.conn.execute('PRAGMA journal_mode = OFF')

    def _closeOutput(self):
        self._startEvent('Closing database')
        self.conn.close()

    def _parseLinkLine(self,count:int,line: str):
        #stripped = line.replace('INSERT INTO `pagelinks` VALUES ','')
        #sql = unicode(line, errors='replace')
        sql = line.replace("""\\\\\\\\',""","\',")
        sql = sql.replace("""\\\\',""","\',")
        sql = sql.replace("""\\\'""","''")
        sql = sql.replace('''\\\"''','''"''')
        
        try:
            self.conn.execute(sql)
            self.conn.commit()
        except sqlite3.Error as e:
            self._report('ERROR', 'Unable to parse line nr: {}'.format(count))
            print(e)
            with open(self.parameters.error_file,'a') as err_file:
                err_file.write('\n\nerror:\n')
                err_file.write(e.__str__())
                err_file.write('\nline nr:\n')
                err_file.write(str(count))
                err_file.write('\nline:\n')
                err_file.write(line)
                err_file.write('\nSQL:\n')
                err_file.write(sql)
        finally:
            if (count % 100) == 0:
                self._report('INFO','Processed link line: {}'.format(count))
    
    def _importPages(self):
        self._startEvent('Page import')
        count = 0
        to_db = []
        with open(self.parameters.input_page_file, encoding='utf-8', errors='replace') as in_file:
            for line in in_file:
                count += 1
                fields = line.split(':')
                nr_fields = len(fields)
                if  nr_fields >= 3:
                    # some titles have a : in the title, that causes a problem in the import
                    remain_cleaned = ':'.join(fields[2:]).rstrip()
                    #self.out_file.write('{}:{}'.format(fields[1],remain_cleaned))
                    to_db.append([fields[1],remain_cleaned])
                else:
                    self._report('ERROR', 'page import: less than 3 fields in line nr {}'.format(count))

        if len(to_db) > 0:
            sql = "INSERT INTO pages VALUES (?,?);"
            self.conn.executemany(sql,to_db)
            self.conn.commit()
        else:
            self._report('ERROR', 'page import: No valid fields to import.')
        self._endEvent('Page import')

def loadParameters(configFilename):
    with open(configFilename, 'r') as f:
        config = json.load(f)

    return ParametersWiki2Sqlite(**config)

def writeSampleConfig():
    param = ParametersWiki2Sqlite(
        input_file      = 'nlwiki-latest-pagelinks.sql',
        input_page_file = 'nlwiki-latest-pages-articles-multistream-index.txt',
        output_file     = 'pagelinks.db',
        error_file      = 'error.txt'
    )

    #write it back to the file
    with open('example_config.json', 'w') as f:
        json.dump(param.__dict__, fp=f, indent=4)

def main():
    parser = ArgumentParser(description="Convert wiki dumpfiles to sqlite database\n")
    parser.add_argument("--file", "-f", help="Filename of the config file, config.json if not specified", type=str, required=False, default='config.json')
    parser.add_argument("--config", "-c", help="Write an example config file named example_config.json",action='store_true')
    #parser.add_argument("--help", "-h", help="show the help text",action='store_true')
    args = parser.parse_args()

    if args.config:
        writeSampleConfig()
    elif hasattr(args, 'help') and args.help:
        parser.print_help()
    else:
        parameters=loadParameters(args.file)
        converter = Wiki2Sqlite(parameters)
        converter.convert()

if __name__ == '__main__':  
    main()