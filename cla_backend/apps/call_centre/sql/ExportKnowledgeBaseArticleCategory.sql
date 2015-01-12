COPY (SELECT
id,
created,
modified,
name
FROM knowledgebase_articlecategory
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/knowledgebase_articlecategory.csv' CSV HEADER;
