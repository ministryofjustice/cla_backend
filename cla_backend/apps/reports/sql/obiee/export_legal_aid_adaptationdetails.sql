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
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO STDOUT CSV HEADER;
