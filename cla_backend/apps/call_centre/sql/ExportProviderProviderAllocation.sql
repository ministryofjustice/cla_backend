COPY (SELECT
id,
created,
modified,
provider_id,
category_id,
weighted_distribution
FROM cla_provider_providerallocation
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/cla_provider_providerallocation.csv' CSV HEADER;
