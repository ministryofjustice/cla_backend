COPY (SELECT
id,
created,
modified,
case_id,
alternative_help_article_id,
assigned_by_id
FROM legalaid_caseknowledgebaseassignment
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO STDOUT CSV HEADER;
