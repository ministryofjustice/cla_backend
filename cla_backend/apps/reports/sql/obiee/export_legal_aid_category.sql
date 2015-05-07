COPY (SELECT
id,
created,
modified,
name,
code,
raw_description,
ecf_available,
mandatory,
description,
'order'
FROM legalaid_category
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
