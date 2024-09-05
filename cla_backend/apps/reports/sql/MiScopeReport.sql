WITH log_changed_category as (
    SELECT log_created.case_id, (log_changed_category.patch #>> '{}')::json#>>'{backwards,0,value}' as "diagnosis_category"
    FROM cla_eventlog_log as log_created
    JOIN cla_eventlog_log as log_changed_category ON log_created.case_id=log_changed_category.case_id
        AND log_created.notes = 'Case created digitally' AND log_changed_category.notes LIKE 'Changed category to%%'
),
log_mi_oos_outcome_code as (
    SELECT case_id, code
    FROM cla_eventlog_log
    WHERE code = 'MIS-OOS'
    GROUP BY case_id, code
)

SELECT
  c.personal_details_id as "Person ID"
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
     WHEN ec.state NOT IN('yes', 'no') THEN 'Pending'
     WHEN ec.state IS NOT NULL AND provider_assigned_at IS NULL THEN 'Operator'
     WHEN c.provider_viewed IS NOT NULL AND log_mi_oos_outcome_code.code IS NULL THEN 'Read and approved by SP'
     WHEN c.provider_viewed IS NOT NULL AND log_mi_oos_outcome_code.code IS NOT NULL THEN 'Read and NOT approved by SP'
    ELSE 'Provider has not viewed'
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
LEFT OUTER JOIN log_changed_category ON log_changed_category.case_id = c.id
LEFT OUTER JOIN legalaid_mattertype as mt1 on mt1.id = c.matter_type1_id
LEFT OUTER JOIN legalaid_mattertype as mt2 on mt2.id = c.matter_type2_id
LEFT OUTER JOIN diagnosis_diagnosistraversal as diagnosis on c.diagnosis_id = diagnosis.id
LEFT OUTER JOIN log_mi_oos_outcome_code ON log_mi_oos_outcome_code.case_id = c.id
ORDER BY c.modified DESC
