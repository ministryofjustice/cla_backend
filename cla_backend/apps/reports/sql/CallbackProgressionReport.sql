SELECT
  c.reference as Case_Ref
  ,c.requires_action_at::date as callback_date
  ,TO_CHAR(c.requires_action_at, 'HH24:MI') AS callback_slot
  ,c.source
  ,c.outcome_code as Callback_Type
  ,CASE WHEN c.thirdparty_details_id IS NOT NULL THEN 'Y' ELSE 'N' END AS third_party
  ,c.created::date as case_created_date
  ,TO_CHAR(c.created, 'HH24:MI') AS case_created_time
FROM legalaid_case c
WHERE c.requires_action_at::date >= %(from_date)s
  AND c.requires_action_at::date < %(to_date)s
ORDER BY c.requires_action_at
