COPY (SELECT
id,
name
FROM auth_group)
TO '{path}/auth_group.csv' CSV HEADER;
