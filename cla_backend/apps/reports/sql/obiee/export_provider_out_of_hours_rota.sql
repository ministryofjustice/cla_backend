COPY (SELECT
id,
created,
modified,
start_date,
end_date,
category_id,
provider_id
FROM cla_provider_outofhoursrota
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
