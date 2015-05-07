COPY (SELECT
id,
created,
modified,
personal_details_id,
'[deleted]' AS pass_phrase,
reason,
personal_relationship,
personal_relationship_note,
spoke_to,
no_contact_reason,
organisation_name,
reference
FROM legalaid_thirdpartydetails
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
