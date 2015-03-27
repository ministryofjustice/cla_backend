COPY (SELECT
id,
user_id,
group_id
FROM auth_user_groups)
TO STDOUT CSV HEADER;
