SELECT
    c.laa_reference,
    c.reference,
    category.code,
    c.created,
    p.full_name,
    p.date_of_birth,
    p.postcode
FROM legalaid_case AS c
    LEFT OUTER JOIN diagnosis_diagnosistraversal AS diagnosis ON c.diagnosis_id = diagnosis.id
    LEFT OUTER JOIN legalaid_category AS category ON diagnosis.category_id = category.id
    JOIN legalaid_personaldetails AS p ON p.id = c.personal_details_id
WHERE
    c.created >= %s AND c.created < %s
    AND
    -- filter out where name+dob+postcode appears more than once in the date range
    concat(
        regexp_replace(lower(p.full_name), '[^a-z]', ''),
        '§§',
        to_char(p.date_of_birth, 'YYYYMMDD'),
        '§§',
        regexp_replace(lower(p.postcode), '[^0-9a-z]', ''))
    IN (
        SELECT concat(
            regexp_replace(lower(p2.full_name), '[^a-z]', ''),
            '§§',
            to_char(p2.date_of_birth, 'YYYYMMDD'),
            '§§',
            regexp_replace(lower(p2.postcode), '[^0-9a-z]', '')) AS discriminator
        FROM legalaid_personaldetails AS p2
        GROUP BY discriminator
        HAVING COUNT(*) > 1)
ORDER BY
    -- order groups together
    concat(
        regexp_replace(lower(p.full_name), '[^a-z]', ''),
        '§§',
        to_char(p.date_of_birth, 'YYYYMMDD'),
        '§§',
        regexp_replace(lower(p.postcode), '[^0-9a-z]', '')),
    c.created DESC;
