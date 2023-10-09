WITH latest_outcome as (
    select
      e.*
      ,row_number() over (PARTITION BY e.case_id order by e.id desc) as rn
    FROM legalaid_case c
      join cla_eventlog_log e on e.case_id = c.id
    where
      e.type = 'outcome'

),
    operator_first_access as (
      SELECT e.*
        ,row_number() over (PARTITION BY e.case_id order by e.id asc) as rn
      FROM
        cla_eventlog_log as e
        JOIN auth_user as u on e.created_by_id = u.id
        JOIN call_centre_operator as op on u.id = op.user_id
      WHERE
        e.code != 'CASE_CREATED'

  ),
    operator_first_action as (
      SELECT e.*
        ,row_number() over (PARTITION BY e.case_id order by e.id asc) as rn
      FROM
        cla_eventlog_log as e
        JOIN auth_user as u on e.created_by_id = u.id
        JOIN call_centre_operator as op on u.id = op.user_id
      WHERE
        e.code != 'CASE_CREATED'
        and e.level >= 29
  ),
    provider_first_view as (
      SELECT
        e.*
        ,row_number() over (PARTITION BY e.case_id order by e.id asc) as rn
      FROM
        cla_eventlog_log AS e
        JOIN auth_user AS u ON e.created_by_id = u.id
        JOIN cla_provider_staff AS staff ON u.id = staff.user_id
      WHERE
        e.code != 'CASE_CREATED'

  ), provider_first_assign as (
    SELECT
      e.*
      ,row_number() over (PARTITION BY e.case_id order by e.id asc) as rn
    FROM
      cla_eventlog_log AS e
    WHERE
      e.code  in ('REFSP', 'MANALC', 'MANREF', 'SPOR')

)
select
  c.laa_reference as "LAA_Reference"
  ,md5(lower(regexp_replace((pd.full_name||pd.postcode)::text, '\s', '', 'ig'))) as "Hash_ID"
  ,c.reference as "Case_ID"
  ,COALESCE(assigned_provider.name, trim((log.context->'provider')::text, '"'), provider.name) as "Provider_ID" -- need to convert to LAA provider ID
  ,category.code as "Category_Name"
  ,c.created as "Date_Case_Created"
  ,mt1.code as "Matter_Type_1"
  ,mt2.code as "Matter_Type_2"
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
  ,CASE
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) <= 24 THEN 'A'
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) <= 29 THEN 'B'
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) <= 39 THEN 'C'
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) <= 49 THEN 'D'
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) <= 59 THEN 'E'
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) <= 79 THEN 'F'
      WHEN EXTRACT(YEAR from age(now(), pd.date_of_birth)) >= 80 THEN 'G'
      WHEN pd.date_of_birth IS NULL THEN 'U'
      END as "Age(Range)"
  ,mc.code as "Media_Code"
  ,c.source as "Contact_Type"
  ,null as "Referral_Agencies"
  ,c.exempt_user_reason as "Exempt_Client"
  ,CASE upper(adapt.language) 
    WHEN upper('Welsh') THEN true 
    ELSE false 
  END as "Welsh"
  ,CASE upper(adapt.language)
    WHEN 'ENGLISH' THEN 'English'
    WHEN 'WELSH' THEN 'ENGLISH'
    WHEN '' THEN 'Null'
    ELSE 'Non-English'
    END as "Language"
  ,log.created as "Outcome_Created_At"
  ,c.thirdparty_details_id::bool as "Has_Third_Party"
  ,cc_org.name as "Organisation"
  ,c.notes as "Notes"
  ,c.provider_notes as "Provider Notes"
  ,adapt.notes as "Adaptation Notes"
  ,pd.vulnerable_user as "Vulnerable User"
  ,CASE 
    WHEN TRIM('123456789' FROM SUBSTRING(pd.postcode, 1, 2)) IN ('DE', 'LE', 'LN', 'NG') THEN 'East Midlands'
    WHEN TRIM('123456789' FROM SUBSTRING(pd.postcode, 1, 2)) IN ('AL', 'CB', 'CM', 'CO', 'HP', 'IP', 'LU', 'NR', 'SG', 'SS') THEN 'East of England'
    WHEN TRIM('123456789' FROM SUBSTRING(pd.postcode, 1, 2)) IN ('BR', 'CR', 'DA', 'E', 'EC', 'EN', 'HA', 'IG', 'KT', 'N', 'NW', 'RM', 'SE', 'SM', 'SW', 'TW', 'UB', 'W', 'WC', 'WD') THEN 'Greater London'
    WHEN TRIM('123456789' FROM SUBSTRING(pd.postcode, 1, 2)) IN ('DH', 'DL', 'NE', 'SR', 'TS') THEN 'North East'
    WHEN TRIM('123456789' FROM SUBSTRING(pd.postcode, 1, 2)) IN ('BB', 'BD', 'BL', 'CA', 'CH', 'CW', 'FY', 'HD', 'L', 'LA', 'M', 'OL', 'PR', 'SK', 'WA', 'WN') THEN 'North West'
    WHEN TRIM('123456789' FROM SUBSTRING(pd.postcode, 1, 2)) IN ('DN', 'HD', 'HG', 'HU', 'HX', 'LS', 'S', 'WF', 'YO') THEN 'Yorkshire and Humber'
    WHEN TRIM('123456789' FROM SUBSTRING(pd.postcode, 1, 2)) IN ('BN', 'CT', 'GU', 'ME', 'MK', 'OX', 'PO', 'RG', 'RH', 'SL', 'SO', 'TN') THEN 'South East'
    WHEN TRIM('123456789' FROM SUBSTRING(pd.postcode, 1, 2)) IN ('BA', 'BH', 'BS', 'DT', 'EX', 'GL', 'PL', 'SN', 'SP', 'TA', 'TQ', 'TR') THEN 'South West'
    WHEN TRIM('123456789' FROM SUBSTRING(pd.postcode, 1, 2)) IN ('CF', 'LD', 'LL', 'NP', 'SA', 'SY') THEN 'Wales'
    WHEN TRIM('123456789' FROM SUBSTRING(pd.postcode, 1, 2)) IN ('B', 'CV', 'DY', 'HR', 'NN', 'ST', 'TF', 'WR', 'WS', 'WV') THEN 'West Midlands'
    ELSE 'NA'
  END as "Geographical_region"
  -- diversity fields --
  ,{diversity_expression} as diversity_json
from cla_eventlog_log as log
  JOIN legalaid_case as c on c.id = log.case_id and not (c.eligibility_check_id is null and c.diagnosis_id is null and personal_details_id is null)
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
  LEFT OUTER JOIN latest_outcome on latest_outcome.case_id = c.id and latest_outcome.rn = 1
  LEFT OUTER JOIN operator_first_action on operator_first_action.case_id = c.id and operator_first_action.rn = 1
  LEFT OUTER JOIN operator_first_access on operator_first_access.case_id = c.id and operator_first_access.rn = 1
  LEFT OUTER JOIN provider_first_view on provider_first_view.case_id = c.id and provider_first_view.rn = 1
  LEFT OUTER JOIN provider_first_assign on provider_first_assign.case_id = c.id and provider_first_assign.rn = 1
  LEFT OUTER JOIN legalaid_case split_case on c.from_case_id = split_case.id
  LEFT OUTER JOIN cla_provider_provider as assigned_provider on (log.context->>'provider_id')::numeric = assigned_provider.id
  LEFT OUTER JOIN call_centre_organisation AS cc_org ON cc_org.id = c.organisation_id
where
  log.type = 'outcome'
  and log.created >= %s
  and log.created < %s
GROUP BY "Geographical_region"
