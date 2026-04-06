
import requests
import bz2
import gzip
import shutil


class WikiDownload:

    def __init__(self,lang:str='nl'):
        self.lang = lang
        self.base_url = f'https://dumps.wikimedia.org/{self.lang}wiki/latest/{self.lang}'
        self.page_list_url = f'{self.base_url}wiki-latest-pages-articles-multistream-index.txt.bz2'
        self.page_links_url = f'{self.base_url}wiki-latest-pagelinks.sql.gz'
        self.link_target_url = f'{self.base_url}wiki-latest-linktarget.sql.gz'

    def _download_url(self,url:str):
        params = {'stream':True}
        local_filename = url.split('/')[-1]
        
        print(f'Download {local_filename} started')
        response = requests.get(url, params=params)

        total_bits = 0
        if response.status_code == 200:
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        total_bits += 1024
                        f.write(chunk)
        print(f'Download {local_filename} ready')

    def download(self):
        self._download_url(self.page_list_url)
        self._download_url(self.page_links_url)
        self._download_url(self.link_target_url)

    def _decompress_bz2(self,filename:str):
        print(f'Decompressing {filename}')
        new_filename = filename.replace('.bz2','')
        with open(new_filename, 'wb') as new_file, open(filename, 'rb') as input_file:
            decompressor = bz2.BZ2Decompressor()
            for data in iter(lambda : input_file.read(100 * 1024), b''):
                new_file.write(decompressor.decompress(data))
        print(f'Decompressed {filename} to {new_filename}')
    
    def _decompress_gz(self,filename:str):
        print(f'Decompressing {filename}')
        new_filename = filename.replace('.gz','')
        with gzip.open(filename, 'rb') as input_file:
            with open(new_filename, 'wb') as output_file:
                shutil.copyfileobj(input_file, output_file)
        print(f'Decompressed {filename} to {new_filename}')

    def decompress_page_list(self):
        local_filename = self.page_list_url.split('/')[-1]
        self._decompress_bz2(local_filename)
    
    def decompress_page_links(self):
        local_filename = self.page_links_url.split('/')[-1]
        self._decompress_gz(local_filename)

    def decompress_link_target(self):
        local_filename = self.link_target_url.split('/')[-1]
        self._decompress_gz(local_filename)
    

def main():
    downloader = WikiDownload()
    downloader.download()
    downloader.decompress_page_list()
    downloader.decompress_page_links()
    downloader.decompress_link_target()


if __name__ == '__main__':
    main()
