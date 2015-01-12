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
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/cla_provider_staff.csv' CSV HEADER;
