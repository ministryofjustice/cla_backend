COPY (SELECT
id,
created,
modified,
provider_id,
created_by_id,
'[deleted]' AS comment,
'[deleted]' AS body,
month
FROM cla_provider_csvupload
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/cla_provider_csvupload.csv' CSV HEADER;
