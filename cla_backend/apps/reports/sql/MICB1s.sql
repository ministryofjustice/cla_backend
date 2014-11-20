WITH  latest_outcome as (
    select
      e.*
    FROM legalaid_case c
      join cla_eventlog_log e on e.case_id = c.id

    where  e.id = (
      SELECT MAX(l.id) FROM cla_eventlog_log l WHERE
        l.case_id = c.id
        and l.type = 'outcome'
      group by l.case_id)

), operator_first_view as (
    SELECT e.* FROM
      cla_eventlog_log as e

    WHERE
      e.id = (SELECT MIN(l.id) FROM cla_eventlog_log l
        JOIN auth_user as u on l.created_by_id = u.id
        JOIN call_centre_operator as op on u.id = op.user_id
      WHERE l.case_id = e.case_id
            and l.code != 'CASE_CREATED'
      group by l.case_id)
),
    operator_first_outcome AS (
      SELECT
        e.*
      FROM
        cla_eventlog_log AS e

      WHERE
        e.id = (
          SELECT
            MIN(l.id)
          FROM cla_eventlog_log l
            JOIN auth_user AS u ON l.created_by_id = u.id
            JOIN call_centre_operator AS op ON u.id = op.user_id
          WHERE l.case_id = e.case_id

                AND l.id > (SELECT
                              MAX(ll.id)
                            FROM cla_eventlog_log ll
                            WHERE ll.case_id = l.case_id
                                  AND ll.code = 'CB1'
          )
                and l.code != 'CASE_VIEWED'
          GROUP BY l.case_id)
  ),

    operator_first_log_after_cb1 AS (
      SELECT
        e.*
      FROM
        cla_eventlog_log AS e

      WHERE
        e.id = (
          SELECT
            MIN(l.id)
          FROM cla_eventlog_log l
            JOIN auth_user AS u ON l.created_by_id = u.id
            JOIN call_centre_operator AS op ON u.id = op.user_id
          WHERE l.case_id = e.case_id

                AND l.id > (SELECT
                              MAX(ll.id)
                            FROM cla_eventlog_log ll
                            WHERE ll.case_id = l.case_id
                                  AND ll.code = 'CB1'
          )
                and l.code = 'CASE_VIEWED'
          GROUP BY l.case_id)
  )
select
   c.laa_reference as "LAA_Reference"
  ,md5(lower(regexp_replace((pd.full_name||pd.postcode)::text, '\s', '', 'ig'))) as "Hash_ID_personal_details_captured"
  ,c.reference as "Case_ID"
  ,provider.name "Provider_ID_if_allocated"
  ,category.code as "Law_Category_Name"
  ,c.created as "Date_Case_Created"
  ,c.modified as "Last_Modified_Date"
  ,log.code as "Outcome_Code_Child"
  ,CASE WHEN log.code = 'NCOE' THEN 0 ELSE ceil(EXTRACT(EPOCH FROM (timer.stopped - timer.created))) END as "Billable_Time"
  ,mt1.code as "Matter_Type_1"
  ,mt2.code as "Matter_Type_2"
  ,CASE WHEN op.id IS NOT NULL THEN 'OS:'||log.created_by_id::text
   END as "User_ID"
  ,CASE diagnosis.state
   when 'INSCOPE' then 'PASS'
   when 'OUTOFSCOPE' then 'FAIL'
   else 'UNKNOWN'
   END as "Scope_Status"
  ,CASE ec.state
   when 'yes' then 'PASS'
   when 'no' then 'FAIL'
   else 'UNKNOWN'
   END as "Eligibility_Status"
  ,ceil(EXTRACT(EPOCH FROM operator_first_view.created-c.created)) as "Time_to_OS_Access"
  ,log.created as "Outcome_Created_At"
  ,u.username as "Username"
  ,c.requires_action_at as "Requires_Action_At"
  ,log.notes as "Log_Notes"
  ,ceil(EXTRACT(EPOCH FROM operator_first_log_after_cb1.created-c.requires_action_at)) as "Time_to_view_after_requires_action_at"
  ,ceil(EXTRACT(EPOCH FROM operator_first_outcome.created-c.requires_action_at)) as "Time_to_action_after_requires_action_at"
  ,operator_first_log_after_cb1.created-c.requires_action_at as "Time_to_view_after_requires_action_at_for_humans"
  ,operator_first_outcome.created-c.requires_action_at as "Time_to_action_after_requires_action_at_for_humans"
  ,operator_first_outcome.code as "Next_Outcome"
from cla_eventlog_log as log
  JOIN legalaid_case as c on c.id = log.case_id
  LEFT OUTER JOIN legalaid_personaldetails as pd on c.personal_details_id = pd.id
  LEFT OUTER JOIN cla_provider_provider as provider on c.provider_id = provider.id
  LEFT OUTER JOIN diagnosis_diagnosistraversal as diagnosis on c.diagnosis_id = diagnosis.id
  LEFT OUTER JOIN legalaid_category as category on diagnosis.category_id = category.id
  LEFT OUTER JOIN timer_timer as timer on log.timer_id = timer.id and timer.stopped IS NOT null and timer.cancelled = false
  LEFT OUTER JOIN legalaid_mattertype as mt1 on mt1.id = c.matter_type1_id
  LEFT OUTER JOIN legalaid_mattertype as mt2 on mt2.id = c.matter_type2_id
  LEFT OUTER JOIN legalaid_eligibilitycheck as ec on c.eligibility_check_id = ec.id
  LEFT OUTER JOIN legalaid_adaptationdetails as adapt on c.adaptation_details_id = adapt.id
  LEFT OUTER JOIN auth_user as u on log.created_by_id = u.id
  LEFT OUTER JOIN call_centre_operator as op on u.id = op.user_id
  LEFT OUTER JOIN legalaid_mediacode as mc on mc.id = c.media_code_id
  LEFT OUTER JOIN latest_outcome on latest_outcome.case_id = c.id
  LEFT OUTER JOIN operator_first_view on operator_first_view.case_id = c.id
  LEFT OUTER JOIN operator_first_log_after_cb1 on operator_first_log_after_cb1.case_id = c.id
  LEFT OUTER JOIN operator_first_outcome on operator_first_outcome.case_id = c.id
  LEFT OUTER JOIN legalaid_case split_case on c.from_case_id = split_case.id

where
  log.type = 'outcome'
  and log.created < now()
  and log.created >= %s
  and log.created < %s
  and log.code in ('CB1')
  and c.requires_action_at IS NOT NULL;
