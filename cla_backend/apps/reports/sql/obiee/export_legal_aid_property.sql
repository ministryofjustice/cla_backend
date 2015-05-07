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
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
