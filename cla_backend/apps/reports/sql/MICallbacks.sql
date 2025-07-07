SELECT lc.reference as "Case ref",
       (cel.context->>'requires_action_at')::timestamp::date AS "Callback date",
       TO_CHAR((cel.context->>'requires_action_at')::timestamp, 'HH24:MI') AS "Callback time",
       lc.source as "Case source",
       cel.code as "Callback code",
       CASE
           WHEN lc.source = 'WEB' THEN 'Client'
           ELSE 'Operator'
    END as "Callback requested by",
    CASE
        WHEN lc.callback_type = 'web_form_third_party' THEN 'Y'
        ELSE 'N'
    END as "Third Party bypass",
    cel.created::date as "Request made date",
    TO_CHAR((cel.created)::timestamp, 'HH24:MI:SS') as "Request made time",
    CASE
        WHEN source = 'WEB' THEN ccbts.capacity
        ELSE NULL
    END as "Interval cap"
FROM cla_eventlog_log cel
JOIN legalaid_case lc ON cel.case_id = lc.id
LEFT JOIN checker_callbacktimeslot ccbts ON ccbts.date = (cel.context->>'requires_action_at')::timestamp::date AND ccbts.time = TO_CHAR((cel.context->>'requires_action_at')::timestamp, 'HH24MI')
WHERE code IN ('CB1', 'CB2', 'CB3')
    AND
    (
        (lc.modified >= %(from_date)s AND lc.modified <= %(to_date)s)
                    OR
        (lc.created >= %(from_date)s AND lc.created <= %(to_date)s)
    )
ORDER by (cel.context->>'requires_action_at')::timestamp DESC
