COPY (SELECT
id,
created,
modified,
group_id,
name,
code
FROM legalaid_mediacode
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
