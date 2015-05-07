COPY (
    SELECT pd.id
        ,pd.created
        ,pd.modified
        ,'[deleted]' AS title
        ,'[deleted]' AS full_name
        -- remove last two characters of postcode so as to not uniquely ID anyone
        ,left(replace(upper(pd.postcode), ' ', ''), -2) AS postcode
        ,'[deleted]' AS street
        ,'[deleted]' AS mobile_phone
        ,'[deleted]' AS home_phone
        ,pd.reference
        ,'[deleted]' AS email
        ,pd.date_of_birth
        ,'[deleted]' AS ni_number
        ,pd.contact_for_research
        ,pd.vulnerable_user
        ,pd.safe_to_contact
        ,pd.case_count
        ,pd.safe_to_email
        ,pd.diversity_modified
        ,trim((dv.diversity->'gender')::text, '"') AS diversity_gender
        ,trim((dv.diversity->'sexual_orientation')::text, '"') AS diversity_sexual_orientation
        ,trim((dv.diversity->'disability')::text, '"') AS diversity_disability
        ,trim((dv.diversity->'ethnicity')::text, '"') AS diversity_ethnicity
        ,trim((dv.diversity->'religion')::text, '"') AS diversity_religion
    FROM legalaid_personaldetails AS pd
    JOIN (select id, {diversity_expression} as diversity
          from legalaid_personaldetails) as dv on pd.id = dv.id
    WHERE (pd.modified >= %(from_date)s::timestamp AND pd.modified <= %(to_date)s::timestamp)
    OR (pd.created >= %(from_date)s::timestamp AND pd.created <= %(to_date)s::timestamp)
)
TO STDOUT CSV HEADER;
