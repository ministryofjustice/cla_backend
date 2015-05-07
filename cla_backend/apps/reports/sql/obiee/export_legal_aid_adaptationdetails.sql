COPY (SELECT
id,
created,
modified,
bsl_webcam,
minicom,
text_relay,
skype_webcam,
language,
'[deleted]' AS notes,
callback_preference,
reference
FROM legalaid_adaptationdetails
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
