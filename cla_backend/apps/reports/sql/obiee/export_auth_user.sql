COPY (SELECT
id,
'[deleted]' AS password,
last_login,
is_superuser,
username,
first_name,
last_name,
email,
is_staff,
is_active,
date_joined
FROM auth_user
WHERE date_joined >= %(from_date)s::timestamp AND date_joined <= %(to_date)s::timestamp)
TO STDOUT CSV HEADER;
