SELECT
  c.laa_reference as "LAA_Reference"
, f.created as "Date_Feedback_Created"
, f.issue as "Feedback_Issue"
, f.justified as "Feedback_Justified"
, f.resolved as "Feedback_Resolved"
, f.comment as "Text_Output"
, category.code as "Category"
, p.name as "Provider name"
, u.email as "User email"
  from cla_provider_feedback as f
  JOIN legalaid_case as c on f.case_id = c.id
  JOIN cla_provider_staff as s on f.created_by_id = s.id
  JOIN auth_user as u on s.user_id = u.id
  JOIN cla_provider_provider as p on s.provider_id = p.id
  LEFT OUTER JOIN diagnosis_diagnosistraversal as diagnosis on c.diagnosis_id = diagnosis.id
  LEFT OUTER JOIN legalaid_category as category on diagnosis.category_id = category.id
where
  f.created >= %s
  and f.created < %s
