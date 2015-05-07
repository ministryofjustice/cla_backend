COPY (SELECT
id,
created,
modified,
organisation,
service_name,
description,
website,
keywords,
when_to_use,
geographic_coverage,
type_of_service,
resource_type,
address,
opening_hours,
how_to_use,
accessibility
FROM knowledgebase_article
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
