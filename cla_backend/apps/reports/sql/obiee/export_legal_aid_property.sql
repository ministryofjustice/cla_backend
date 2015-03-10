COPY (SELECT
id,
created,
modified,
value,
mortgage_left,
share,
eligibility_check_id,
disputed,
main
FROM legalaid_property
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO STDOUT CSV HEADER;
