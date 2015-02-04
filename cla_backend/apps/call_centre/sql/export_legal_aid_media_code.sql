COPY (SELECT
id,
created,
modified,
group_id,
name,
code
FROM legalaid_mediacode
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO STDOUT CSV HEADER;
