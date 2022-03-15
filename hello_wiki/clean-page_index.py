from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class ParametersPageParser:
    input_file:     str
    output_file:    str

class PageParser:

    def __init__(self, parameters: ParametersPageParser):
        self.parameters = parameters
        self.out_file = None

    def parse(self):
        self._openOutput()
        count = 0
        with open(self.parameters.input_file, encoding='utf-8') as in_file:
            while True:
                count += 1
                line = in_file.readline()
                if not line:
                    break
                self._parseLine(count,line)
        self._closeOutput()

    def _openOutput(self):
        out_file = Path(self.parameters.output_file)
        if out_file.exists():
            os.remove(self.parameters.output_file)
        self.out_file = open(self.parameters.output_file,'w')

    def _closeOutput(self):
        self.out_file.close()

    def _parseLine(self,count:int,line: str):
        fields = line.split(':')
        nr_fields = len(fields)
        if  nr_fields >= 3:
            # some titles have a : in the title, that causes a problem in the import
            remain_cleaned = ' _ '.join(fields[2:])
            self.out_file.write('{}:{}'.format(fields[1],remain_cleaned))
        else:
            print('ERROR: less than 3 fields in line nr {}'.format(count))


def main():
    param = ParametersPageParser(
        input_file  = '/home/fvbakel/tmp/wiki-data/nlwiki-20220301-pages-articles-multistream-index.txt',
        output_file = '/home/fvbakel/tmp/wiki-data/pagelinks-clean.txt'
    )
    parser = PageParser(param)
    parser.parse()

if __name__ == '__main__':
    main()