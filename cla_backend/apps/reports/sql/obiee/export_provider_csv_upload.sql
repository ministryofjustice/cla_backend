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
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
