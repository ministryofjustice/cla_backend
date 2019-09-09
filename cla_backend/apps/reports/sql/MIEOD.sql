SELECT
    c.laa_reference,
    c.reference,
    category.code,
    -- eod.created,
    eod.modified,
    eod_cat.category,
    eod.notes,
    UPPER(CAST(eod_cat.is_major as TEXT)),
    cc_org.name as organisation
    -- is_escalated is unknown currently
    -- is_resolved is unknown currently
    -- is_justified is unknown currently
FROM legalaid_eoddetails AS eod
    LEFT OUTER JOIN legalaid_eoddetailscategory as eod_cat ON eod_cat.eod_details_id = eod.id
    JOIN legalaid_case AS c ON c.id = eod.case_id
    LEFT OUTER JOIN diagnosis_diagnosistraversal AS diagnosis ON c.diagnosis_id = diagnosis.id
    LEFT OUTER JOIN legalaid_category AS category ON diagnosis.category_id = category.id
    LEFT OUTER JOIN call_centre_organisation AS cc_org ON cc_org.id = c.organisation_id
WHERE c.created >= %s AND c.created < %s
ORDER BY c.created DESC;
