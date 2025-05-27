WITH rfc as (
    SELECT string_agg(crfc_cat.category, ', ') as cats, case_id
    FROM checker_reasonforcontacting crfc
    JOIN checker_reasonforcontactingcategory crfc_cat on crfc.id = crfc_cat.reason_for_contacting_id
    GROUP BY case_id
)
SELECT lc.reference as "Case ref", lc.created as "Case created date", lc.modified as "Case modified date",
   CONCAT(cst.financial_assessment_status, ' + ', cst.fast_track_reason) as "Contact type",
    rfc.cats as "Enquiry contact reason",
    lc.callback_type as "Callback type",
    lc.client_notes as "Client notes",
    lc.outcome_code as "CHS outcome code",
    lc.is_urgent as "Urgent"
FROM legalaid_case lc
JOIN legalaid_personaldetails pd ON pd.id = lc.personal_details_id
JOIN checker_scopetraversal cst ON cst.id = lc.scope_traversal_id
LEFT JOIN rfc ON rfc.case_id = lc.id
WHERE source='WEB'

