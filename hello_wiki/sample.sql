-- simple select from pages
select * from pages where title = 'Riethoven';
-- result: 280719|Riethoven
 
-- select links to Riethoven
select * from linktarget where lt_title = 'Riethoven';
-- result: 423120|0|Riethoven

-- select the pages that link to this page
select count(*) 
from pagelinks 
where pl_target_id = 423120;

-- result 114, from different namespaces

-- namespace 0 is the main namespace we are interested in
select 
    p.title  as from_title,
    lt.lt_title as to_title
    from pagelinks l
    left join linktarget lt on lt.lt_id = l.pl_target_id
    left join pages p on p.page_id = l.pl_from  
 where 
        l.pl_namespace = 0 and
        lt.lt_namespace = 0 and
        lt.lt_title = 'Riethoven'
;

/* Start all post processing in manual steps

*/
select count(*) from linktarget where lt_namespace != 0;
-- before: 3.216.936
select count(*) from pagelinks where pl_namespace != 0;
-- before: 30.161.910

-- so we can drop all the namespace = 0 records
-- from both tables
delete from linktarget where lt_namespace != 0;

delete from pagelinks where pl_namespace != 0;

-- cleanup the database after these mass deletes
vacuum;
.exit 
-- step 1 done
-- make indexes


create index i_linktarget_tmp 
    on linktarget(lt_title)
;

create index i_linktarget_tmp_id
    on linktarget(lt_id)
;

create index i_pages 
    on pages (page_id)
;

create index i_pages_title
    on pages (title)
;

create index i_pagelinks_target_id_tmp
    on pagelinks (pl_target_id)
;

create table pagelinks_clean as
    SELECT 
        l.pl_from       as pl_from,
        p_to.page_id    as pl_to
    from pagelinks l
        join linktarget lt on lt.lt_id = l.pl_target_id
        join pages p_from on p_from.page_id = l.pl_from
        join pages p_to on p_to.title = replace(lt.lt_title,'_',' ')
;

drop table pagelinks;

alter table pagelinks_clean rename to pagelinks;

drop table linktarget;

create index i_pagelinks_from
    on pagelinks(pl_from,pl_to)
;

create index i_pagelinks_to
    on pagelinks(pl_to,pl_from)
;

vacuum;

/* End all post processing in manual steps

-- new counts after namespace cleanup
select count(*) from linktarget;
-- before: 9.822.438     after: 6.605.502
select count(*) from pagelinks;
-- before: 126.030.098   after: 95.868.188

--
-- Find all from pagelinks that pl_from is not in pages
-- statement takes too long .... :-(
SELECT count(*) FROM pagelinks l
    left join pages p on p.page_id = l.pl_from
WHERE
    p.page_id is NULL
;

-- results in   81.723.159
-- original has 98.551.055
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

