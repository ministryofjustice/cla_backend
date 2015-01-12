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
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/legalaid_category.csv' CSV HEADER;
