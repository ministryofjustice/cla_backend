WITH diversity_view as (
  select id, {diversity_expression} as diversity
--   select id, '{}'::json as diversity
  from legalaid_personaldetails
), latest_outcome as (
    select
      e.*
      FROM legalaid_case c
      join cla_eventlog_log e on e.case_id = c.id

    where  e.id = (
      SELECT MAX(l.id) FROM cla_eventlog_log l WHERE
        l.case_id = c.id
        and l.type = 'outcome'
      group by l.case_id)

),
operator_first_access as (
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
operator_first_action as (
    SELECT e.* FROM
      cla_eventlog_log as e

    WHERE
      e.id = (SELECT MIN(l.id) FROM cla_eventlog_log l
        JOIN auth_user as u on l.created_by_id = u.id
        JOIN call_centre_operator as op on u.id = op.user_id
      WHERE l.case_id = e.case_id
            and l.code != 'CASE_CREATED'
            and l.level >= 29
      group by l.case_id)


),
    provider_first_view as (
    SELECT
      e.*
    FROM
      cla_eventlog_log AS e
    WHERE
      e.id = (SELECT
                MIN(l.id)
              FROM cla_eventlog_log l
                JOIN auth_user AS u ON l.created_by_id = u.id
                JOIN cla_provider_staff AS staff ON u.id = staff.user_id
              WHERE l.case_id = e.case_id
                    AND l.code != 'CASE_CREATED'
              GROUP BY l.case_id)
), provider_first_assign as (
    SELECT
      e.*
    FROM
      cla_eventlog_log AS e
    WHERE
      e.id = (SELECT
                MIN(l.id)
              FROM cla_eventlog_log l
              WHERE l.case_id = e.case_id
                    AND l.code  in ('REFSP', 'MANALC', 'MANREF', 'SPOR')
              GROUP BY l.case_id)
)
select
  c.laa_reference as "LAA_Reference"
  ,md5(lower(regexp_replace((pd.full_name||pd.postcode)::text, '\s', '', 'ig'))) as "Hash_ID"
  ,c.reference as "Case_ID"
  -- SPLIT FIELDS. --
  ,c.from_case_id::boolean as "Split_Check"
  ,split_case.laa_reference as "Split_Link_Case"
  -- /SPLIT FIELDS. --
  ,COALESCE(assigned_provider.name, trim((log.context->'provider')::text, '"'), provider.name) as "Provider_ID" -- need to convert to LAA provider ID
  ,category.code as "Category_Name"
  ,c.created as "Date_Case_Created"
  ,c.modified as "Last_Modified_Date"
  ,log.code as "Outcome_Code_Child"
  ,CASE WHEN log.code = 'NCOE' THEN 0 ELSE ceil(EXTRACT(EPOCH FROM (timer.stopped - timer.created))) END as "Billable_Time"
  ,CASE WHEN latest_outcome.id = log.id THEN c.billable_time ELSE null END as "Cumulative_Time"
  ,mt1.code as "Matter_Type_1"
  ,mt2.code as "Matter_Type_2"
  ,CASE WHEN op.id IS NOT NULL THEN 'OS:'||log.created_by_id::text
        WHEN staff.id IS NOT NULL THEN 'SP:'||log.created_by_id::text
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
  ,COALESCE(adapt.bsl_webcam, false)::bool as "Adjustments_BSL"
  ,CASE upper(COALESCE(adapt.language, ''))
      WHEN upper('English') THEN false
      WHEN upper('Welsh') THEN false
      WHEN '' THEN false
      ELSE true
   END as "Adjustments_LLI"
  ,COALESCE(adapt.minicom, false)::bool as "Adjustments_MIN"
  ,COALESCE(adapt.text_relay, false)::bool as "Adjustments_TYP"
  ,COALESCE(adapt.callback_preference, false)::bool as "Adjustments_CallbackPreferred"
  ,COALESCE(adapt.skype_webcam, false)::bool as "Adjustments_Skype"
  -- diversity fields --
  ,trim((diversity_view.diversity->'gender')::text, '"') as "Gender"
  ,trim((diversity_view.diversity->'ethnicity')::text, '"') as "Ethnicity"
  ,CASE
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) <= 20 THEN 'A'
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) <= 30 THEN 'B'
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) <= 40 THEN 'C'
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) <= 50 THEN 'D'
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) <= 60 THEN 'E'
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) <= 70 THEN 'F'
      WHEN pd.date_of_birth IS NULL THEN 'U'
      ELSE 'G'
      END as "Age(Range)"
  ,trim((diversity_view.diversity->'religion')::text, '"') as "Religion"
  ,trim((diversity_view.diversity->'sexual_orientation')::text, '"') as "Sexual_Orientation"
  ,trim((diversity_view.diversity->'disability')::text, '"') as "Disability"
  -- / diversity fields --
  ,CASE
    when EXTRACT(DOW from c.created at time zone 'Europe/London') = 5 and EXTRACT(HOUR from c.created at time zone 'Europe/London') >= 20 then 'WKEND' -- after 20:00 on friday
    when EXTRACT(DOW from c.created at time zone 'Europe/London') = 6 and (EXTRACT(HOUR from c.created at time zone 'Europe/London') < 12 OR (EXTRACT(HOUR from c.created at time zone 'Europe/London') = 12 AND EXTRACT(MINUTE from c.created at time zone 'Europe/London') < 30))  then 'WKEND' -- saturday before 12:30
    when EXTRACT(DOW from c.created at time zone 'Europe/London') = 6 and (EXTRACT(HOUR from c.created at time zone 'Europe/London') > 12 OR (EXTRACT(HOUR from c.created at time zone 'Europe/London') = 12 AND EXTRACT(MINUTE from c.created at time zone 'Europe/London') < 30))  then '9TO5' -- saturday after 12:30
    when EXTRACT(HOUR from c.created at time zone 'Europe/London') between 0 and 16 then '9TO5' -- weekday normal hours
    when EXTRACT(HOUR from c.created at time zone 'Europe/London')  between 17 and 19 and not EXTRACT(DOW from c.created at time zone 'Europe/London') in (6,0)  then '5TO8' -- weekday out of hours
    when EXTRACT(HOUR from c.created at time zone 'Europe/London') >= 20 and not EXTRACT(DOW from c.created at time zone 'Europe/London') = 5 then '9TO5' -- weekday after 20:00
    ELSE '9TO5'
   END as "Time_of_Day"
  ,CASE
     WHEN log.code = 'COI' OR strpos(log.code, 'MIS') = 1 THEN log.code
     ELSE null
   END as "Reject_Reason"
  ,mc.code as "Media_Code"
  ,c.source as "Contact_Type"
  ,null as "Call_Back_Request_Time"
  ,null as "Call_Back_Actioned_Time"
  ,ceil(EXTRACT(EPOCH FROM operator_first_access.created-c.created)) as "Time_to_OS_Access"
  ,ceil(EXTRACT(EPOCH FROM provider_first_view.created-provider_first_assign.created))  as "Time_to_SP_Access"
  ,'PASS' as "Residency_Test"
  ,null as "Repeat_Contact"
  ,null as "Referral_Agencies"
  ,null as "Complaint_Type"
  ,null as "Complaint_Date"
  ,null as "Complaint_Owner"
  ,null as "Complaint_Target"
  ,null as "Complaint_Subject"
  ,null as "Complaint_Classification"
  ,null as "Complaint_Outcome"
  ,pd.contact_for_research as "Agree_Feedback"
  ,c.exempt_user_reason as "Exempt_Client"
  ,CASE upper(adapt.language) WHEN upper('Welsh') THEN true ELSE false END as "Has_Language"
  ,adapt.language as "Language"
  ,log.created as "Outcome_Created_At"
  ,u.username as "Username"
  ,c.thirdparty_details_id::bool as "Has_Third_Party"
  ,ceil(EXTRACT(EPOCH FROM operator_first_action.created-c.created)) as "Time_to_OS_Action"
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
  LEFT OUTER JOIN cla_provider_staff as staff on u.id = staff.user_id
  LEFT OUTER JOIN legalaid_mediacode as mc on mc.id = c.media_code_id
  LEFT OUTER JOIN latest_outcome on latest_outcome.case_id = c.id
  LEFT OUTER JOIN operator_first_action on operator_first_action.case_id = c.id
  LEFT OUTER JOIN operator_first_access on operator_first_access.case_id = c.id
  LEFT OUTER JOIN provider_first_view on provider_first_view.case_id = c.id
  LEFT OUTER JOIN provider_first_assign on provider_first_assign.case_id = c.id
  LEFT OUTER JOIN legalaid_case split_case on c.from_case_id = split_case.id
  LEFT OUTER JOIN diversity_view on pd.id = diversity_view.id
  LEFT OUTER JOIN cla_provider_provider as assigned_provider on trim((log.context->'provider_id')::text, '"')::numeric = assigned_provider.id

where
  log.type = 'outcome'
  and log.created >= %s
  and log.created < %s
