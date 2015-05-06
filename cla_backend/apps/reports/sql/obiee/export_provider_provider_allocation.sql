COPY (SELECT
id,
created,
modified,
provider_id,
category_id,
weighted_distribution
FROM cla_provider_providerallocation
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
