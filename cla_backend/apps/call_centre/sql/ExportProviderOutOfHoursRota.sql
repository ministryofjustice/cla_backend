COPY (SELECT
id,
created,
modified,
start_date,
end_date,
category_id,
provider_id
FROM cla_provider_outofhoursrota
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/cla_provider_outofhoursrota.csv' CSV HEADER;
