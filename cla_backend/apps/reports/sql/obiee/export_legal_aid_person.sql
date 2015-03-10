COPY (SELECT
id,
created,
modified,
income_id,
savings_id,
deductions_id
FROM legalaid_person
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO STDOUT CSV HEADER;
