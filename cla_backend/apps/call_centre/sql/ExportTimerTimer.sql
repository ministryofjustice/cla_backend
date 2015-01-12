COPY (SELECT
id,
created,
modified,
created_by_id,
stopped,
linked_case_id,
cancelled
FROM timer_timer
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/timer_timer.csv' CSV HEADER;
