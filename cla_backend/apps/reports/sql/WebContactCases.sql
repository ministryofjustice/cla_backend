WITH rfc as (
    SELECT string_agg(crfc_cat.category, ', ' order by crfc_cat.category) as cats, case_id
    FROM checker_reasonforcontacting crfc
    JOIN legalaid_case lc ON crfc.case_id = lc.id
    JOIN checker_reasonforcontactingcategory crfc_cat on crfc.id = crfc_cat.reason_for_contacting_id
    WHERE
        (lc.modified >= %(from_date)s AND lc.modified <= %(to_date)s)
            OR
        (lc.created >= %(from_date)s AND lc.created <= %(to_date)s)
    GROUP BY case_id
)
SELECT lc.reference as "Case ref", lc.created as "Case created date", lc.modified as "Case modified date",
    CASE
        WHEN cst.financial_assessment_status IS NOT NULL THEN CONCAT(cst.financial_assessment_status, ' + ', cst.fast_track_reason)
        ELSE cst.fast_track_reason
    END as "Contact type",
    rfc.cats as "Enquiry contact reason",
    lc.callback_type as "Callback type",
    lc.client_notes as "Client notes",
    lc.outcome_code as "CHS outcome code",
    lc.is_urgent as "Urgent"
FROM legalaid_case lc
JOIN checker_scopetraversal cst ON cst.id = lc.scope_traversal_id
JOIN cla_eventlog_log cel on lc.id = cel.case_id AND cel.notes LIKE 'Case created digitally'
LEFT JOIN rfc ON rfc.case_id = lc.id
WHERE
        (lc.modified >= %(from_date)s AND lc.modified <= %(to_date)s)
            OR
        (lc.created >= %(from_date)s AND lc.created <= %(to_date)s)

ORDER BY lc.created DESC
