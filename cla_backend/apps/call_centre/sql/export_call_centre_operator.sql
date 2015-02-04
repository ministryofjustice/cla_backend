COPY (SELECT
id,
created,
modified,
user_id,
is_manager,
is_cla_superuser
FROM call_centre_operator
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO STDOUT CSV HEADER;
