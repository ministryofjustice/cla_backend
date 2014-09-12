SELECT
  c.laa_reference as "LAA_Reference"
, f.created as "Date_Feedback_Created"
, f.issue as "Feedback_Issue"
, f.justified as "Feedback_Justified"
, f.resolved as "Feedback_Resolved"
, f.comment as "Text_Output"
  from cla_provider_feedback as f
  join legalaid_case as c on f.case_id = c.id
where
  f.created >= %s
  and f.created < %s
