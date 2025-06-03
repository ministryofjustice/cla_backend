WITH rfc as (
    SELECT string_agg(crfc_cat.category, ', ' order by crfc.id) as cats, case_id
    FROM checker_reasonforcontacting crfc
    JOIN checker_reasonforcontactingcategory crfc_cat on crfc.id = crfc_cat.reason_for_contacting_id
    GROUP BY case_id
),
valid_creators as (
    SELECT auth_user.id
    FROM auth_user
    LEFT JOIN call_centre_operator cco ON auth_user.id = cco.user_id
    WHERE cco.id IS NOT NULL OR auth_user.username = 'web'
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
JOIN valid_creators vc ON vc.id = lc.created_by_id
LEFT JOIN cla_eventlog_log cel ON cel.case_id = lc.id AND cel.code = 'CB1'
LEFT JOIN checker_scopetraversal cst ON cst.id = lc.scope_traversal_id
LEFT JOIN rfc ON rfc.case_id = lc.id
WHERE
    (
    -- Web cases that are I will call you back: No callback is created in the event log
        (lc.callback_type IS NULL AND cst.id IS NOT NULL)
    -- Call me or someone else web cases
        OR cel.id is NOT NULL
    )
    AND(
        (lc.modified >= %(from_date)s:: timestamp AND lc.modified <= %(to_date)s:: timestamp)
            OR
        (lc.created >= %(from_date)s:: timestamp AND lc.created <= %(to_date)s:: timestamp)
    )
ORDER BY lc.created DESC
