COPY (SELECT
id,
created,
modified,
case_id,
timer_id,
code,
type,
level,
created_by_id,
'[deleted]' AS notes,
'[deleted]' AS patch,
context
FROM cla_eventlog_log
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO STDOUT CSV HEADER;
