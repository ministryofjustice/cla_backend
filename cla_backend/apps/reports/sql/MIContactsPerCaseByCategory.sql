SELECT
  c.reference
  ,c.laa_reference
  ,count(log.id) as "outcome_count"
  ,category.code as "category"
  ,c.created as "created"
  ,array_to_string(array_agg(log.code), '|') as "outcomes"
from
cla_eventlog_log as log
  JOIN legalaid_case as c on c.id = log.case_id
  LEFT OUTER JOIN diagnosis_diagnosistraversal as diagnosis on c.diagnosis_id = diagnosis.id
  FULL OUTER JOIN legalaid_category as category on diagnosis.category_id = category.id

  WHERE
    true
    and c.created >= %s
    and c.created < %s
    and log.code = ANY(%s)

  GROUP BY c.reference
    ,c.laa_reference
    ,category.code
    ,c.created
