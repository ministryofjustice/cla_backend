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
helpline,
geographic_coverage,
type_of_service,
resource_type,
address,
opening_hours,
how_to_use,
accessibility
FROM knowledgebase_article
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/knowledgebase_article.csv' CSV HEADER;
