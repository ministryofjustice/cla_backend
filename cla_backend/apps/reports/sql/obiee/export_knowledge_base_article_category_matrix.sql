COPY (SELECT
id,
created,
modified,
article_id,
article_category_id,
preferred_signpost
FROM knowledgebase_articlecategorymatrix
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
