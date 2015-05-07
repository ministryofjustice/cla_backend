COPY (SELECT
id,
created,
modified,
income_id,
savings_id,
deductions_id
FROM legalaid_person
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
