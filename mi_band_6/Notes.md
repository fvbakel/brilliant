# Notes

## SQL to get basic data

```SQL
SELECT 
    "TIMESTAMP",datetime("TIMESTAMP",'unixepoch','localtime') as DATETIME, 
    HEART_RATE, 
    ("TIMESTAMP"- LAG("TIMESTAMP") OVER())/60 as TIME_DIFF
FROM MI_BAND_ACTIVITY_SAMPLE
WHERE HEART_RATE<>255 and HEART_RATE > 0 
;

```

## Daily minimum

```SQL
select 
    strftime('%Y.%m.%d', datetime(timestamp, 'unixepoch')) as d,
    min(HEART_RATE) as MIN_HEART_RATE 
from MI_BAND_ACTIVITY_SAMPLE 
WHERE HEART_RATE<>255 and HEART_RATE > 0 
group by d
;
```

## Big changes in heart rate

```SQL
SELECT 
    H           as HOUR,
    count(H)    as NUMBER_OF_PEAKS
FROM (
    SELECT 
        "TIMESTAMP",datetime("TIMESTAMP",'unixepoch','localtime')       as DATE_TIME, 
        strftime('%H', datetime(timestamp, 'unixepoch','localtime'))    as H,
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
    and TIME_DIFF = 1
group by H
;
```


## Based on

[https://github.com/Freeyourgadget/Gadgetbridge/wiki/Data-Export-Import-Merging-Processing#user-content-backup-your-data](https://github.com/Freeyourgadget/Gadgetbridge/wiki/Data-Export-Import-Merging-Processing#user-content-backup-your-data)

