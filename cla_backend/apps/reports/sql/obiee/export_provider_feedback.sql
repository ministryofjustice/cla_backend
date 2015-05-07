COPY (SELECT
id,
created,
modified,
reference,
case_id,
created_by_id,
'[deleted]' AS comment,
justified,
resolved,
issue
FROM cla_provider_feedback
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
