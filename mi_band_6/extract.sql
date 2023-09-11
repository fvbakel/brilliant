.separator ;
.header on
.output raw.csv
SELECT 
    "TIMESTAMP",datetime("TIMESTAMP",'unixepoch','localtime')       as DATE_TIME, 
    strftime('%H', datetime(timestamp, 'unixepoch','localtime'))    as H,
    strftime('%m', datetime(timestamp, 'unixepoch','localtime'))    as M,
    (LAG("HEART_RATE") OVER())                                      as PREVIOUS_HEART_RATE,
    ("TIMESTAMP"- LAG("TIMESTAMP") OVER())/60                       as TIME_DIFF,
    ("HEART_RATE"- LAG("HEART_RATE") OVER())                        as HEART_RATE_DIFF,
    HEART_RATE
FROM 
    MI_BAND_ACTIVITY_SAMPLE
WHERE 
        HEART_RATE <> 255 
    and HEART_RATE > 0 
order BY
    TIMESTAMP asc
;
