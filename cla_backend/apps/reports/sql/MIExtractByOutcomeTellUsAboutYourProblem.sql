WITH log_changed_category as (
    SELECT log_created.case_id, (log_changed_category.patch #>> '{}')::json#>>'{backwards,0,value}' as "diagnosis_category"
    FROM cla_eventlog_log as log_created
    JOIN cla_eventlog_log as log_changed_category ON log_created.case_id=log_changed_category.case_id
        AND log_created.notes = 'Case created digitally' AND log_changed_category.notes LIKE 'Changed category to%%'
)
SELECT
  c.personal_details_id as "Personal Details Id"
  ,c.reference as "Case Id"
  ,to_char(c.created, 'YYYY-MM-DD') as "Created"
  ,to_char(c.modified, 'YYYY-MM-DD') as "Modified"
  ,ec.notes as "Diagnosis Notes"
  ,c.notes as "Operator Notes"
  ,c.provider_notes as "Provider Notes"
  ,COALESCE(adapt.bsl_webcam, false)::bool as "Adjustments BSL Webcam"
  ,COALESCE(adapt.callback_preference, false)::bool as "Adjustments Callback Preference"
  ,CASE upper(COALESCE(adapt.language, ''))
      WHEN upper('English') THEN false
      WHEN upper('Welsh') THEN false
      WHEN '' THEN false
      ELSE true
   END as "Adjustments Language"
   ,COALESCE(adapt.no_adaptations_required, false)::bool as "Adjustments Not required"
  ,COALESCE(adapt.minicom, false)::bool as "Adjustments Minicom"
  ,COALESCE(adapt.text_relay, false)::bool as "Adjustments Text Relay"
  ,COALESCE(adapt.skype_webcam, false)::bool as "Adjustments Skype"
  ,COALESCE(log_changed_category.diagnosis_category, category.code) as "Diagnosis Category"
  ,category.code as "Legalaid Category Code"
  ,category.name as "Legalaid Category Name"
  ,c.outcome_code as "Outcome Code"
FROM legalaid_case as c
LEFT OUTER JOIN legalaid_eligibilitycheck as ec on c.eligibility_check_id = ec.id
LEFT OUTER JOIN legalaid_category as category on ec.category_id = category.id
LEFT OUTER JOIN legalaid_adaptationdetails as adapt on c.adaptation_details_id = adapt.id
LEFT OUTER JOIN log_changed_category ON log_changed_category.case_id = c.id
WHERE c.modified >= %(from_date)s AND c.modified < %(to_date)s
ORDER BY c.modified DESC
