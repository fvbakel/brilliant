-- data extract
SELECT 
    "TIMESTAMP",datetime("TIMESTAMP",'unixepoch','localtime')       as DATE_TIME, 
    strftime('%H', datetime(timestamp, 'unixepoch','localtime'))    as H,
    strftime('%m', datetime(timestamp, 'unixepoch','localtime'))    as M,
    (LAG("HEART_RATE") OVER())                                      as PREVIOUS_HEART_RATE,
    HEART_RATE, 
    ("TIMESTAMP"- LAG("TIMESTAMP") OVER())/60                       as TIME_DIFF,
    ("HEART_RATE"- LAG("HEART_RATE") OVER())                        as HEART_RATE_DIFF
FROM 
    MI_BAND_ACTIVITY_SAMPLE
WHERE 
        HEART_RATE <> 255 
    and HEART_RATE > 0 
;


-- SQLite
SELECT 
    H           as HOUR,
    M           as MONTH,
    count(*)    as NUMBER_OF_PEAKS
FROM (
    SELECT 
        "TIMESTAMP",datetime("TIMESTAMP",'unixepoch','localtime')       as DATE_TIME, 
        strftime('%H', datetime(timestamp, 'unixepoch','localtime'))    as H,
        strftime('%m', datetime(timestamp, 'unixepoch','localtime'))    as M,
        (LAG("HEART_RATE") OVER())                                      as PREVIOUS_HEART_RATE,
        HEART_RATE, 
        ("TIMESTAMP"- LAG("TIMESTAMP") OVER())/60                       as TIME_DIFF,
        ("HEART_RATE"- LAG("HEART_RATE") OVER())                        as HEART_RATE_DIFF
    FROM 
        MI_BAND_ACTIVITY_SAMPLE
    WHERE 
            HEART_RATE <> 255 
        and HEART_RATE > 0 
)
WHERE 
        ( HEART_RATE_DIFF > 25 or HEART_RATE_DIFF < -25)
    --and TIME_DIFF = 1
group by 
    H,
    M
order BY
    M,
    H
;

-- number of rapid HR changes per month
SELECT 
    M           as MONTH,
    case
      when HEART_RATE_DIFF < 0 then 'DOWN'
      else 'UP'
    end as DIRECTION,
    count(*)    as NUMBER_OF_PEAKS
FROM (
    SELECT 
        "TIMESTAMP",datetime("TIMESTAMP",'unixepoch','localtime')       as DATE_TIME, 
        strftime('%m', datetime(timestamp, 'unixepoch','localtime'))    as M,
        (LAG("HEART_RATE") OVER())                                      as PREVIOUS_HEART_RATE,
        HEART_RATE, 
        ("TIMESTAMP"- LAG("TIMESTAMP") OVER())/60                       as TIME_DIFF,
        ("HEART_RATE"- LAG("HEART_RATE") OVER())                        as HEART_RATE_DIFF
    FROM 
        MI_BAND_ACTIVITY_SAMPLE
    WHERE 
            HEART_RATE <> 255 
        and HEART_RATE > 0 
)
WHERE 
		ABS(HEART_RATE_DIFF) > 45 
    and TIME_DIFF = 1
group by 
    M,
	DIRECTION
order BY
    M,
	DIRECTION
;



SELECT
    max(strftime('%m', datetime(timestamp, 'unixepoch','localtime')))    as M
FROM 
    MI_BAND_ACTIVITY_SAMPLE
WHERE 
        HEART_RATE <> 255 
    and HEART_RATE > 0  
;