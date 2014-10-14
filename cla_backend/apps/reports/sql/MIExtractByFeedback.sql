SELECT
  c.laa_reference as "LAA_Reference"
, f.created as "Date_Feedback_Created"
, f.issue as "Feedback_Issue"
, f.justified as "Feedback_Justified"
, f.resolved as "Feedback_Resolved"
, f.comment as "Text_Output"
, category.code as "Category"
  from cla_provider_feedback as f
  JOIN legalaid_case as c on f.case_id = c.id
  LEFT OUTER JOIN diagnosis_diagnosistraversal as diagnosis on c.diagnosis_id = diagnosis.id
  LEFT OUTER JOIN legalaid_category as category on diagnosis.category_id = category.id
where
  f.created >= %s
  and f.created < %s
