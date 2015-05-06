COPY (SELECT
id,
created,
modified,
reference,
nodes,
current_node_id,
graph_version,
state,
category_id
FROM diagnosis_diagnosistraversal
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
