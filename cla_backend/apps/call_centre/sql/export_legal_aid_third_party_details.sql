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
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO STDOUT CSV HEADER;
