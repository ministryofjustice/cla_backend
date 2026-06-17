SELECT
    c.reference AS case_reference,
    trim((log.context->'requires_action_at')::text, '"')::timestamptz::date AS callback_date,
    TO_CHAR(trim((log.context->'requires_action_at')::text, '"')::timestamptz, 'HH24:MI') AS booking_slot,
    c.source,
    log.code AS callback_type,
    CASE WHEN c.thirdparty_details_id IS NOT NULL THEN 'Y' ELSE 'N' END AS third_party,
    log.created::date AS created_on,
    TO_CHAR(log.created, 'HH24:MI') AS created_at
FROM cla_eventlog_log log
JOIN legalaid_case c ON c.id = log.case_id
WHERE log.code IN ('CB1', 'CB2', 'CB3', 'CB4')
  AND trim((log.context->'requires_action_at')::text, '"')::timestamptz::date >= %(from_date)s
  AND trim((log.context->'requires_action_at')::text, '"')::timestamptz::date < %(to_date)s
ORDER BY c.reference, log.created