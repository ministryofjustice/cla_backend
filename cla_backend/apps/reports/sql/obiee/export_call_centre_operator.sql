COPY (SELECT
id,
created,
modified,
user_id,
is_manager,
is_cla_superuser
FROM call_centre_operator
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
