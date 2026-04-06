# Wiki relation analyzer

This program can be used to analyze the relation between pages from wikipedia. It should work on all languages, but ith was tested for the dutch (```nl```) wiki pages.

## Required data

This program requires the following data dumps to be downloaded from
[https://dumps.wikimedia.org](https://dumps.wikimedia.org/).

1. List of all pages, in the format of ```pages-articles-multistream-index.txt```. For example:
[https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-pages-articles-multistream-index.txt.bz2](https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-pages-articles-multistream-index.txt.bz2)
2. A SQL dump of the ```pagelinks``` table, ```pagelinks.sql```. For example: [https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-pagelinks.sql.gz](https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-pagelinks.sql.gz)
3. A SQL dump if the ```linktarget``` table. For example: [https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-linktarget.sql.gz](https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-linktarget.sql.gz)

The download an decompressing of these file can be done with the steps below:

1. ```mkdir wiki_download```
2. ```cd wiki_download```
3. ```python3 download_wiki.py```

The ```pages-articles-multistream-index.txt``` file contains lines in the format ```offset1:pageId1:title1```. For example: ```216556046:280719:Riethoven```. The offset is ignored in the import.

The ```pagelinks```  table is explained [here](https://www.mediawiki.org/wiki/Manual:Pagelinks_table)

You can create a link to wikipage based on the ```page_id```. For example: [https://nl.wikipedia.org/?curid=280719](https://nl.wikipedia.org/?curid=280719)


## Steps to create the database

Take the following steps:

1. Download the required data and extract in an folder.
2. Create a config file template: ```python3 wikiPagelinks2sqlite.py -c```
3. Edit ```example_config.json``` to your needs and save as ```config.json```
4. Run: ```python3 wikiPagelinks2sqlite.py -f your_config.json```
5. This will create the sqlite database

## The database

The database has two tables:

1. ```pages```
2. ```pagelinks```

The example below illustrates how the two tables can be used.

```SQL
select 
    l.pl_from  as pl_from,
    l.pl_title as to_title,
    'https://nl.wikipedia.org/?curid=' || l.pl_from as link
    from pagelinks l
    left join pages p on p.page_id = l.pl_from
 where 
        l.pl_title = 'Riethoven'
;
```

The file ```sample.sql``` contains more sample sql statements that can be used to query the local wiki database.

## Find path

The program ```findPath.py``` uses the created database to analyze how two pages are related.

Examples:

- ```python3 findPath.py config```
- ```python3 findPath.py top```
- ```python3 findPath.py path Riethoven Westerhoven```