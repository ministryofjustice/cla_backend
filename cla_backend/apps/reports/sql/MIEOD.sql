SELECT
    c.laa_reference,
    c.reference,
    category.code,
    -- eod.created,
    eod.modified,
    eod_cat.category,
    eod.notes,
    UPPER(CAST(eod_cat.is_major as TEXT))
    -- is_escalated is unknown currently
    -- is_resolved is unknown currently
    -- is_justified is unknown currently
FROM legalaid_eoddetails AS eod
    LEFT OUTER JOIN legalaid_eoddetailscategory as eod_cat ON eod_cat.eod_details_id = eod.id
    JOIN legalaid_case AS c ON c.eod_details_id = eod.id
    LEFT OUTER JOIN diagnosis_diagnosistraversal AS diagnosis ON c.diagnosis_id = diagnosis.id
    LEFT OUTER JOIN legalaid_category AS category ON diagnosis.category_id = category.id
WHERE c.created >= %s AND c.created < %s
ORDER BY c.created DESC;
