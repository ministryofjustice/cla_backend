COPY (SELECT
id,
created,
modified,
user_id,
provider_id,
is_manager,
'[deleted]' AS chs_organisation,
'[deleted]' AS chs_user,
'[deleted]' AS chs_password
FROM cla_provider_staff
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
