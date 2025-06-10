WITH log_mi_oos_outcome_code as (
    SELECT case_id, code
    FROM cla_eventlog_log
    WHERE code = 'MIS-OOS'
    GROUP BY case_id, code
)

SELECT
   DISTINCT c.personal_details_id as "Person ID"
  ,c.reference as "Case Id"
  ,to_char(c.created, 'YYYY-MM-DD') as "Created"
  ,to_char(c.modified, 'YYYY-MM-DD') as "Modified"
  ,c.source as "Case source"
  ,CASE diagnosis.state
      when 'INSCOPE' then 'INSCOPE'
      else NULL
   END as "CHS scope state"
  ,'' as "Web scope state"
  ,CASE ec.state
      when 'yes' then 'yes'
      when 'no' then 'no'
      else 'unknown'
   END as "Means eligibility state"
  ,CASE
     WHEN diagnosis.state IS NULL OR diagnosis.state = 'UNKNOWN' THEN 'Pending'
     WHEN ec.state IS NOT NULL AND provider_assigned_at IS NULL THEN 'Operator'
      -- All the provider outcome codes that are not MI-OOS
     WHEN c.provider_viewed IS NOT NULL AND log_mi_oos_outcome_code.code IS NULL AND c.outcome_code IN ('MIS-MEANS', 'COI', 'MIS', 'SPOP', 'CLSP', 'DREFER', 'REOPEN', 'REF-EXT', 'REF-INT', 'REF-EXT_CREATED', 'REF-INT_CREATED') THEN 'Read and approved by SP'
     WHEN c.provider_viewed IS NOT NULL AND log_mi_oos_outcome_code.code IS NOT NULL THEN 'Read and NOT approved by SP'
     WHEN c.provider_viewed IS NOT NULL THEN 'Read by SP'
    ELSE 'NOT read by SP'
  END as "Workflow status"
  ,c.outcome_code as "CHS case outcome code"
  ,c.provider_notes as "Provider Notes"
  ,c.notes as "Operator Notes"
  ,ec.notes as "Client notes"
  ,category.code as "Category code"
  ,category.name as "Category name"
  ,mt1.code as "Matter Type 1 code"
  ,mt1.description as "Matter Type 1 description"
  ,mt2.code as "Matter Type 2 code"
  ,mt2.description as "Matter Type 2 description"
  ,'' as "Web diagnosis category 1"
  ,'' as "Web diagnosis category 2"
  ,'' as "Web diagnosis category 3"
  ,'' as "Web diagnosis category 4"
  ,'' as "Web diagnosis category 5"
  ,'' as "Web diagnosis category 6"
FROM legalaid_case as c
LEFT OUTER JOIN legalaid_eligibilitycheck as ec on c.eligibility_check_id = ec.id
LEFT OUTER JOIN legalaid_category as category on ec.category_id = category.id
LEFT OUTER JOIN legalaid_adaptationdetails as adapt on c.adaptation_details_id = adapt.id
LEFT OUTER JOIN legalaid_mattertype as mt1 on mt1.id = c.matter_type1_id
LEFT OUTER JOIN legalaid_mattertype as mt2 on mt2.id = c.matter_type2_id
LEFT OUTER JOIN diagnosis_diagnosistraversal as diagnosis on c.diagnosis_id = diagnosis.id
LEFT OUTER JOIN log_mi_oos_outcome_code ON log_mi_oos_outcome_code.case_id = c.id
WHERE  source IN ('WEB')
AND c.modified >= %(from_date)s AND c.modified < %(to_date)s
ORDER BY to_char(c.modified, 'YYYY-MM-DD') DESC
