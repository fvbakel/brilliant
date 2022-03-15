select 
    p.title    as from_title,
    l.pl_title as to_title
    from pagelinks l
    join pages p on p.page_id = l.pl_from
 where 
    l.pl_title = 'Riethoven'
;

-- Make a link to the pages in pagelink that are not in pages
select 
    l.pl_from  as pl_from,
    l.pl_title as to_title,
    'https://nl.wikipedia.org/?curid=' || l.pl_from as link
    from pagelinks l
    left join pages p on p.page_id = l.pl_from
 where 
        l.pl_title = 'Riethoven'
    and p.title is null
;
-- Conclusion:
-- these pageslink from user personal pages.

--
-- Find all from pagelinks that pl_from is not in pages
-- statement takes too long .... :-(
SELECT count(*) FROM pagelinks l
    left join pages p on p.page_id = l.pl_from
WHERE
    p.page_id is NULL
;

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



