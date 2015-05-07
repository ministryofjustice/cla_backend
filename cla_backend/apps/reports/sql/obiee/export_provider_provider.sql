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
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
