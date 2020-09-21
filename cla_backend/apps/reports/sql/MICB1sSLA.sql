WITH
    operator_first_view_after_cb1 as (
      SELECT
         o.id as o_id
        ,no.id as no_id
        ,no.code as code
        ,log_call_started.code as cs_code
        ,log_call_started.created as cs_created
        ,no.created
        ,row_number() over (PARTITION BY o.id order by no.id asc) as rn
      from cla_eventlog_log o
        JOIN cla_eventlog_log no on
                                   o.case_id = no.case_id
                                   and no.id > o.id
        LEFT JOIN cla_eventlog_log log_call_started on
                                   log_call_started.case_id = no.case_id
                                   and log_call_started.id > o.id
                                   and log_call_started.code = 'CALL_STARTED'
        JOIN call_centre_operator AS op ON no.created_by_id = op.user_id
      order by no.id asc

  ),

    operator_first_log_after_cb1 as (
      SELECT
         o.id as o_id
        ,no.id as no_id
        ,no.code as code
        ,no.created
        ,row_number() over (PARTITION BY o.id order by no.id asc) as rn
      from cla_eventlog_log o
        JOIN cla_eventlog_log no on
                                   o.case_id = no.case_id
                                   and no.id > o.id
        JOIN call_centre_operator AS op ON no.created_by_id = op.user_id
      WHERE no.level >= 29 and no.type in ('outcome', 'event')
      order by no.id asc

  ),
    all_rows as (
      select
         log.id as log_id
        ,c.id
        ,c.laa_reference as "LAA_Reference"
        ,md5(lower(regexp_replace((pd.full_name||pd.postcode)::text, '\s', '', 'ig'))) as "Hash_ID_personal_details_captured"
        ,c.reference as "Case_ID"
        ,provider.name "Provider_ID_if_allocated"
        ,category.code as "Law_Category_Name"
        ,c.created as "Date_Case_Created"
        ,c.modified as "Last_Modified_Date"
        ,log.code as "Outcome_Code_Child"
        ,mt1.code as "Matter_Type_1"
        ,mt2.code as "Matter_Type_2"
        ,log.created_by_id
        ,cs_code
        ,cs_created
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
        ,log.created as "Outcome_Created_At"
        ,u.username as "Username"
        ,operator_first_log_after_cb1.created as operator_first_log_after_cb1__created
        ,operator_first_view_after_cb1.created as operator_first_view_after_cb1__created
        ,c.created as case_created
        ,operator_first_log_after_cb1.code as "Next_Outcome"
        ,trim((log.context->'requires_action_at')::text, '"')::timestamptz as callback_window_start
        ,trim((log.context->'requires_action_at')::text, '"')::timestamptz + interval '30 minutes' as callback_window_end
        ,trim((log.context->'sla_120')::text, '"')::timestamptz as sla_120
        ,trim((log.context->'sla_480')::text, '"')::timestamptz as sla_480
        ,operator_first_log_after_cb1.rn
        ,operator_first_view_after_cb1.rn
        ,c.source
        ,log.code
        ,cc_org.name as organisation
      from cla_eventlog_log as log
        JOIN legalaid_case as c on c.id = log.case_id
        LEFT OUTER JOIN legalaid_personaldetails as pd on c.personal_details_id = pd.id
        LEFT OUTER JOIN cla_provider_provider as provider on c.provider_id = provider.id
        LEFT OUTER JOIN diagnosis_diagnosistraversal as diagnosis on c.diagnosis_id = diagnosis.id
        LEFT OUTER JOIN legalaid_category as category on diagnosis.category_id = category.id
        LEFT OUTER JOIN legalaid_mattertype as mt1 on mt1.id = c.matter_type1_id
        LEFT OUTER JOIN legalaid_mattertype as mt2 on mt2.id = c.matter_type2_id
        LEFT OUTER JOIN legalaid_eligibilitycheck as ec on c.eligibility_check_id = ec.id
        LEFT OUTER JOIN auth_user as u on log.created_by_id = u.id
        LEFT OUTER JOIN operator_first_log_after_cb1 on operator_first_log_after_cb1.o_id = log.id and operator_first_log_after_cb1.rn = 1
        LEFT OUTER JOIN operator_first_view_after_cb1 on operator_first_view_after_cb1.o_id = log.id and operator_first_view_after_cb1.rn = 1
        LEFT OUTER JOIN call_centre_organisation AS cc_org ON cc_org.id = c.organisation_id
      where
        log.code = 'CB1'

  )
select
  "LAA_Reference"
  ,"Hash_ID_personal_details_captured"
  ,"Case_ID"
  ,"Provider_ID_if_allocated"
  ,"Law_Category_Name"
  ,"Date_Case_Created"
  ,"Last_Modified_Date"
  ,"Outcome_Code_Child"
  ,"Matter_Type_1"
  ,"Matter_Type_2"
  ,"created_by_id"
  ,"Scope_Status"
  ,"Eligibility_Status"
  ,"Outcome_Created_At"
  ,"Username"
  ,operator_first_view_after_cb1__created
  ,operator_first_log_after_cb1__created
  ,"Next_Outcome"
  ,callback_window_start
  ,callback_window_end
  ,CASE
   WHEN source IN ('WEB', 'PHONE') AND operator_first_log_after_cb1__created IS NULL AND %(now)s < callback_window_start THEN FALSE
   WHEN source IN ('WEB', 'PHONE') AND operator_first_log_after_cb1__created IS NULL THEN %(now)s  NOT BETWEEN callback_window_start AND callback_window_end
   WHEN source IN ('WEB', 'PHONE') THEN operator_first_log_after_cb1__created NOT BETWEEN callback_window_start AND callback_window_end
   -- User has NOT been contacted and current time is after the SLA1 window for SMS and VOICE MAIL
   WHEN source IN ('SMS', 'VOICEMAIL') AND cs_created IS NULL THEN %(now)s  > sla_120
   -- User has been contacted and contact time is after the SLA1 window for SMS and VOICE MAIL
   ELSE source IN ('SMS', 'VOICEMAIL') AND cs_created > sla_120
   END as missed_sla_1
  ,CASE
   -- User not contacted and current time is after SLA 2
   WHEN source IN ('WEB', 'PHONE') AND cs_code IS NULL AND %(now)s > callback_window_end + interval '72 hours' THEN TRUE
   -- User contacted and contact time is after SLA 2
   WHEN source IN ('WEB', 'PHONE') AND cs_code IS NOT NULL AND operator_first_log_after_cb1__created > callback_window_end + interval '72 hours'  THEN TRUE
   -- Everything else that is a web / phone case is False
   WHEN source IN ('WEB', 'PHONE') THEN FALSE
   -- User has NOT been contacted and current time is after the SLA2 window for SMS and VOICE MAIL
   WHEN source IN ('SMS', 'VOICEMAIL') AND cs_created IS NULL THEN %(now)s  > sla_480
   -- User has been contacted and contact time is after the SLA2 window for SMS and VOICE MAIL
   ELSE source IN ('SMS', 'VOICEMAIL') AND cs_created > sla_480
   END as missed_sla_2
  ,source
  ,code
  ,organisation
  ,sla_480
  ,cs_created
from all_rows
WHERE %(from_date)s < callback_window_start AND callback_window_start < %(to_date)s
;



