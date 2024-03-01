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
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) <= 24 THEN 'A'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) <= 29 THEN 'B'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) <= 39 THEN 'C'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) <= 49 THEN 'D'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) <= 59 THEN 'E'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) <= 79 THEN 'F'
      WHEN EXTRACT(YEAR from age(now(), personal_details.date_of_birth)) >= 80 THEN 'G'
      WHEN personal_details.date_of_birth IS NULL THEN 'U'
    END as "Age(Range)"
FROM legalaid_case AS legalaid_case
    LEFT OUTER JOIN diagnosis_diagnosistraversal AS diagnosis ON legalaid_case.diagnosis_id = diagnosis.id
    LEFT OUTER JOIN legalaid_category AS category ON diagnosis.category_id = category.id
    LEFT OUTER JOIN legalaid_mattertype AS matter_type_1 ON matter_type_1.id = legalaid_case.matter_type1_id
    LEFT OUTER JOIN legalaid_mattertype AS matter_type_2 ON matter_type_2.id = legalaid_case.matter_type2_id
    LEFT OUTER JOIN cla_provider_provider AS legalaid_provider ON legalaid_provider.id = legalaid_case.provider_id
    LEFT OUTER JOIN legalaid_eligibilitycheck as eligibility_check ON eligibility_check.id = legalaid_case.eligibility_check_id
    LEFT OUTER JOIN legalaid_adaptationdetails AS adaptations ON adaptations.id = legalaid_case.adaptation_details_id
    JOIN legalaid_personaldetails AS personal_details ON personal_details.id = legalaid_case.personal_details_id
WHERE
    legalaid_case.created >= %s AND legalaid_case.created < %s