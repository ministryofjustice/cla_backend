COPY (SELECT
id,
created,
modified,
name,
opening_hours,
active,
short_code,
telephone_frontdoor,
telephone_backdoor,
email_address
FROM cla_provider_provider
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/cla_provider_provider.csv' CSV HEADER;
