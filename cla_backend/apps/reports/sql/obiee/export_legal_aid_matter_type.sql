COPY (SELECT
id,
created,
modified,
category_id,
code,
description,
level
FROM legalaid_mattertype
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
