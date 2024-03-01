WITH latest_outcome AS (
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
SELECT
    legalaid_case.laa_reference,
    md5(lower(regexp_replace((personal_details.full_name||personal_details.postcode)::text, '\s', '', 'ig'))) AS "Hash_ID",
    legalaid_case.reference,
    legalaid_provider.name,
    category.code AS "Category_Name",
    legalaid_case.created AS "Date_Case_Created",
    matter_type_1.code AS "Matter_Type_1",
    matter_type_2.code AS "Matter_Type_2",
    CASE diagnosis.state
      when 'INSCOPE' THEN 'PASS'
      when 'OUTOFSCOPE' THEN 'FAIL'
      else 'UNKNOWN'
    END as "Scope_Status",
    CASE eligibility_check.state
      when 'yes' then 'PASS'
      when 'no' then 'FAIL'
      else 'UNKNOWN'
    END as "Eligibility_Status",
    COALESCE(adaptations.bsl_webcam, false)::bool as "Adjustments_BSL",
    CASE upper(COALESCE(adaptations.language, ''))
      WHEN upper('English') THEN false
      WHEN upper('Welsh') THEN false
      WHEN '' THEN false
      ELSE true
    END as "Adjustments_LLI",
    COALESCE(adaptations.minicom, false)::bool as "Adjustments_MIN",
    COALESCE(adaptations.text_relay, false)::bool as "Adjustments_TYP",
    COALESCE(adaptations.callback_preference, false)::bool as "Adjustments_CallbackPreferred",
    COALESCE(adaptations.skype_webcam, false)::bool as "Adjustments_Skype",
    CASE
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) <  18 THEN 'A'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) <= 24 THEN 'B'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) <= 29 THEN 'C'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) <= 39 THEN 'D'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) <= 49 THEN 'E'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) <= 59 THEN 'F'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) >= 79 THEN 'G'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) >  79 THEN 'h'
      WHEN personal_details.date_of_birth IS NULL THEN 'U'
      ELSE 'Null'
    END as "Age(Range)",
    media_code.code as "Media_Code",
    legalaid_case.source as "Contact_Type",
    null as "Referral_Agencies",
    legalaid_case.exempt_user_reason as "Exempt_Client",
    CASE upper(adaptations.language) 
      WHEN upper('Welsh') THEN true 
      ELSE false 
    END as "Welsh",
    CASE upper(adaptations.language)
      WHEN 'ENGLISH' THEN 'English'
      WHEN 'WELSH' THEN 'English'
      WHEN '' THEN 'Null'
      ELSE 'Non-English'
    END as "Language",
    legalaid_case.outcome_code as "Outcome code",
    provider_first_assign as "Outcome_Created_At",
    legalaid_case.thirdparty_details_id::bool as "Has_Third_Party",
    call_centre_organisation.name as "Organisation",
    legalaid_case.notes as "Notes",
    legalaid_case.provider_notes as "Provider Notes",
    adaptations.notes as "Adaptation Notes",
    personal_details.vulnerable_user as "Vulnerable User",
    CASE 
      WHEN TRIM('123456789' FROM SUBSTRING(personal_details.postcode, 1, 2)) IN ('DE', 'LE', 'LN', 'NG') THEN 'East Midlands'
      WHEN TRIM('123456789' FROM SUBSTRING(personal_details.postcode, 1, 2)) IN ('AL', 'CB', 'CM', 'CO', 'HP', 'IP', 'LU', 'NR', 'SG', 'SS') THEN 'East of England'
      WHEN TRIM('123456789' FROM SUBSTRING(personal_details.postcode, 1, 2)) IN ('BR', 'CR', 'DA', 'E', 'EC', 'EN', 'HA', 'IG', 'KT', 'N', 'NW', 'RM', 'SE', 'SM', 'SW', 'TW', 'UB', 'W', 'WC', 'WD') THEN 'Greater London'
      WHEN TRIM('123456789' FROM SUBSTRING(personal_details.postcode, 1, 2)) IN ('DH', 'DL', 'NE', 'SR', 'TS') THEN 'North East'
      WHEN TRIM('123456789' FROM SUBSTRING(personal_details.postcode, 1, 2)) IN ('BB', 'BD', 'BL', 'CA', 'CH', 'CW', 'FY', 'HD', 'L', 'LA', 'M', 'OL', 'PR', 'SK', 'WA', 'WN') THEN 'North West'
      WHEN TRIM('123456789' FROM SUBSTRING(personal_details.postcode, 1, 2)) IN ('DN', 'HD', 'HG', 'HU', 'HX', 'LS', 'S', 'WF', 'YO') THEN 'Yorkshire and Humber'
      WHEN TRIM('123456789' FROM SUBSTRING(personal_details.postcode, 1, 2)) IN ('BN', 'CT', 'GU', 'ME', 'MK', 'OX', 'PO', 'RG', 'RH', 'SL', 'SO', 'TN') THEN 'South East'
      WHEN TRIM('123456789' FROM SUBSTRING(personal_details.postcode, 1, 2)) IN ('BA', 'BH', 'BS', 'DT', 'EX', 'GL', 'PL', 'SN', 'SP', 'TA', 'TQ', 'TR') THEN 'South West'
      WHEN TRIM('123456789' FROM SUBSTRING(personal_details.postcode, 1, 2)) IN ('CF', 'LD', 'LL', 'NP', 'SA', 'SY') THEN 'Wales'
      WHEN TRIM('123456789' FROM SUBSTRING(personal_details.postcode, 1, 2)) IN ('B', 'CV', 'DY', 'HR', 'NN', 'ST', 'TF', 'WR', 'WS', 'WV') THEN 'West Midlands'
      ELSE 'NA'
    END as "Geographical_region",
    personal_details.postcode as "Postcode",
    null as "Procurement area code",
  -- diversity fields --
    {diversity_expression} as diversity_json
FROM legalaid_case AS legalaid_case
    LEFT OUTER JOIN diagnosis_diagnosistraversal AS diagnosis ON legalaid_case.diagnosis_id = diagnosis.id
    LEFT OUTER JOIN legalaid_category AS category ON diagnosis.category_id = category.id
    LEFT OUTER JOIN legalaid_mattertype AS matter_type_1 ON matter_type_1.id = legalaid_case.matter_type1_id
    LEFT OUTER JOIN legalaid_mattertype AS matter_type_2 ON matter_type_2.id = legalaid_case.matter_type2_id
    LEFT OUTER JOIN cla_provider_provider AS legalaid_provider ON legalaid_provider.id = legalaid_case.provider_id
    LEFT OUTER JOIN legalaid_mediacode as media_code on media_code.id = legalaid_case.media_code_id
    LEFT OUTER JOIN legalaid_eligibilitycheck as eligibility_check ON eligibility_check.id = legalaid_case.eligibility_check_id
    LEFT OUTER JOIN legalaid_adaptationdetails AS adaptations ON adaptations.id = legalaid_case.adaptation_details_id
    LEFT OUTER JOIN call_centre_organisation AS call_centre_organisation ON call_centre_organisation.id = legalaid_case.organisation_id
    LEFT OUTER JOIN latest_outcome on latest_outcome.case_id = legalaid_case.id and latest_outcome.rn = 1
    LEFT OUTER JOIN operator_first_action on operator_first_action.case_id = legalaid_case.id and operator_first_action.rn = 1
    LEFT OUTER JOIN operator_first_access on operator_first_access.case_id = legalaid_case.id and operator_first_access.rn = 1
    LEFT OUTER JOIN provider_first_view on provider_first_view.case_id = legalaid_case.id and provider_first_view.rn = 1
    LEFT OUTER JOIN provider_first_assign on provider_first_assign.case_id = legalaid_case.id and provider_first_assign.rn = 1
    JOIN legalaid_personaldetails AS personal_details ON personal_details.id = legalaid_case.personal_details_id
WHERE
    legalaid_case.created >= %s AND legalaid_case.created < %s