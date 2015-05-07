COPY (SELECT
id,
created,
modified,
created_by_id,
stopped,
linked_case_id,
cancelled
FROM timer_timer
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
