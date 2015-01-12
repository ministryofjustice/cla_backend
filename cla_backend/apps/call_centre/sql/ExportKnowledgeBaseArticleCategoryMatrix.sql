COPY (SELECT
id,
created,
modified,
article_id,
article_category_id,
preferred_signpost
FROM knowledgebase_articlecategorymatrix
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/knowledgebase_articlecategorymatrix.csv' CSV HEADER;
