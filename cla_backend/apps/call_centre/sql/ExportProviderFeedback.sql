COPY (SELECT
id,
created,
modified,
reference,
case_id,
created_by_id,
'[deleted]' AS comment,
justified,
resolved,
issue
FROM cla_provider_feedback
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/cla_provider_feedback.csv' CSV HEADER;
