from dataclasses import dataclass
from pathlib import Path
import os
import sqlite3

@dataclass
class ParametersPagelinkParser:
    input_file:     str
    output_file:    str

class PagelinksParser:

    def __init__(self, parameters: ParametersPagelinkParser):
        self.parameters = parameters
        #self.out_file = None
        self.conn = None

    def parse(self):
        self._openOutput()
        count = 0
        with open(self.parameters.input_file, 'r',encoding='utf-8',errors='replace') as in_file:
            for line in in_file:
                count += 1
                if line.startswith('INSERT INTO '):
                    self._parseLine(count,line)
        self._postImport()
        self._closeOutput()

    def _createTable(self):
        sql = """
            CREATE TABLE `pagelinks` (
                `pl_from` int(8) NOT NULL DEFAULT 0,
                `pl_namespace` int(11) NOT NULL DEFAULT 0,
                `pl_title` varbinary(255) NOT NULL DEFAULT '',
                `pl_from_namespace` int(11) NOT NULL DEFAULT 0
            );
        """
        self.conn.execute(sql)
    
    def _postImport(self):
        print('INFO: Post process: create a temp index')
        sql = """
            create index i_pagelinks_tmp 
                on pagelinks(pl_title)
            ;
        """
        self.conn.execute(sql)

        print('INFO: Post process: create new table')
        sql = """
            -- results in   81723159
            -- original has 98551055
            create table pagelinks_clean as
                SELECT 
                    l.pl_from  as pl_from,
                    l.pl_title as pl_title
                    FROM pagelinks l
                    left join pages p on p.page_id = l.pl_from
                WHERE
                    p.page_id is not NULL
            ;
        """

        print('INFO: Post process: dropping temp table')
        sql = """
            drop table pagelinks;
        """
        self.conn.execute(sql)

        print('INFO: Post process: rename table and create a index')
        sql = """
            alter table pagelinks_clean rename to pagelinks;
            create index i_pagelinks_title 
                on pagelinks(pl_title)
            ;
        """
        self.conn.execute(sql)

        print('INFO: Post process: rename table and create a index')
        sql = """
            alter table pagelinks_clean rename to pagelinks;
            create index i_pagelinks_title 
                on pagelinks(pl_title)
            ;
        """
        self.conn.execute(sql)

        print('INFO: Post process: resize (vacuum) database file')
        sql = """
            vacuum;
        """
        self.conn.execute(sql)

    def _openOutput(self):
        #self.out_file = open(self.parameters.output_file,'w')
        db_file = Path(self.parameters.output_file)
        if db_file.exists():
            os.remove(self.parameters.output_file)
        self.conn = sqlite3.connect(self.parameters.output_file)
        self._createTable()


    def _closeOutput(self):
        #self.out_file.close()
        self.conn.close()

    def _parseLine(self,count:int,line: str):
        #stripped = line.replace('INSERT INTO `pagelinks` VALUES ','')
        #sql = unicode(line, errors='replace')
        sql = line.replace("""\\\\',""","\',")
        sql = sql.replace("""\\\'""","''")
        sql = sql.replace('''\\\"''','''"''')
        
        try:
            self.conn.execute(sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print("ERROR: Unable to parse line nr: {}".format(count))
            print(e)
            with open('/home/fvbakel/tmp/wiki-data/debug.txt','a') as err_file:
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
                print("INFO: Processed line: {}".format(count))


def main():
    test_param = ParametersPagelinkParser(
        input_file  = '/home/fvbakel/tmp/wiki-data/head-100-pagelinks.sql',
        output_file = '/home/fvbakel/tmp/wiki-data/head-100-pagelinks.db'
    )

    problem_param = ParametersPagelinkParser(
        input_file  = '/home/fvbakel/tmp/wiki-data/problems.sql',
        output_file = '/home/fvbakel/tmp/wiki-data/problems.db'
    )

    large_param = ParametersPagelinkParser(
        input_file  = '/home/fvbakel/tmp/wiki-data/nlwiki-20220301-pagelinks.sql',
        output_file = '/home/fvbakel/tmp/wiki-data/pagelinks.db'
    )

    parser = PagelinksParser(test_param)
    parser.parse()

if __name__ == '__main__':
    main()