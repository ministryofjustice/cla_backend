COPY (SELECT * FROM legalaid_mediacodegroup)
TO '{path}/public.legalaid_mediacodegroup.csv' CSV HEADER;
