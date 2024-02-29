SELECT
    legalaid_case.laa_reference,
    legalaid_case.reference,
    category.code,
    legalaid_case.created,
    personal_details.full_name,
    personal_details.date_of_birth,
    personal_details.postcode
FROM legalaid_case AS legalaid_case
    LEFT OUTER JOIN diagnosis_diagnosistraversal AS diagnosis ON legalaid_case.diagnosis_id = diagnosis.id
    LEFT OUTER JOIN legalaid_category AS category ON diagnosis.category_id = category.id
    JOIN legalaid_personaldetails AS personal_details ON personal_details.id = legalaid_case.personal_details_id
WHERE
    legalaid_case.created >= %s AND legalaid_case.created < %s