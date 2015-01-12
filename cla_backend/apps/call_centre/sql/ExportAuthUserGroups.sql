COPY (SELECT
id,
user_id,
group_id
FROM auth_user_groups)
TO '{path}/auth_group.csv' CSV HEADER;
