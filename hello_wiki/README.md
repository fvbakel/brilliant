# Wiki relation analyser

## Required data

This program requires the following data dumps to be downloaded from
[https://dumps.wikimedia.org](https://dumps.wikimedia.org/).

1. List of all pages, in the format of ```pages-articles-multistream-index.txt```. For example:
[https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-pages-articles-multistream-index.txt.bz2](https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-pages-articles-multistream-index.txt.bz2)
2. A SQL dump of the ```pagelinks``` table, ```pagelinks.sql```. For example: [https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-pagelinks.sql.gz](https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-pagelinks.sql.gz)

The ```pages-articles-multistream-index.txt``` file contains lines in the format ```offset1:pageId1:title1```. For example: ```216556046:280719:Riethoven```. The offset is ignored in the import.

The ```pagelinks```  table is explained [here](https://www.mediawiki.org/wiki/Manual:Pagelinks_table)

You can create a link to wikipage based on the ```page_id```. For example: [https://nl.wikipedia.org/?curid=280719](https://nl.wikipedia.org/?curid=280719)

## Steps to create the database

Take the following steps:

1. Download the required data and extract in an folder.
2. Create a config file template: ```Python3 wikiPagelinks2sqlie.py -c```
3. Edit ```example_config.json``` to your needs
4. Run: ```Python3 wikiPagelinks2sqlie.py -f your_config.json```
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
