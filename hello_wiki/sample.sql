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


create table pagelinks_clean2 as
    select 
        pl_from,pl_title,p.page_id 
    as pl_to 
    from pagelinks l 
    left join pages p on p.title = replace(l.pl_title,'_',' ')
;

create index i_pagelinks_2 on pagelinks_clean2(pl_from,pl_to);

WITH RECURSIVE
    parameters(start_title,end_title,max_level) as (
        select 
            'Riethoven',
            'Broekhoven',
            1
    ),
    page_ids(start_id,end_id) as (
        select
            (select page_id from pages,parameters where title = parameters.start_title) as start_id,
            (select page_id from pages,parameters where title = parameters.end_title)   as end_id
    )
select * from page_ids
;

WITH RECURSIVE
    sub_rels(child,level,path) AS (
        SELECT 
            280719,
            0,
            '280719'
        UNION ALL
        SELECT 
            rels.pl_to,
            sub_rels.level + 1,
            sub_rels.path || '->' || rels.pl_to
        FROM pagelinks rels, sub_rels
        WHERE 
                rels.pl_from = sub_rels.child
            and sub_rels.level < 2
    )
SELECT sub_rels.path 
FROM sub_rels
--where sub_rels.path like '%1834828%'
--WHERE   sub_rels.child = 1834827
;

WITH RECURSIVE
    parameters(start_title,end_title,max_level) as (
        select 
            'Riethoven',
            'Broekhoven (Bergeijk)',
            2
    ),
    page_ids(start_id,end_id) as (
        select
            (select page_id from pages,parameters where title = parameters.start_title) as start_id,
            (select page_id from pages,parameters where title = parameters.end_title)   as end_id
    ),
    sub_rels(child,level,path) AS (
        SELECT 
            start_id,
            0,
            '' || start_id
            from page_ids
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
    )
SELECT sub_rels.path 
FROM sub_rels,page_ids
WHERE   sub_rels.child = page_ids.end_id
;

