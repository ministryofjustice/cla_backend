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
regexp_replace(notes, E'[\\n\\r\\u2028]+', ' ', 'g')
patch,
context
FROM cla_eventlog_log
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
