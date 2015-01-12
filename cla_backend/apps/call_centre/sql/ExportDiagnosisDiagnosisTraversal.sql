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
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/diagnosis_diagnosistraversal.csv' CSV HEADER;
