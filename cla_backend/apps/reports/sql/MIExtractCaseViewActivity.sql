SELECT lc.reference, log.created as "viewed", auth.username, org.name as organisation
FROM cla_eventlog_log log
  INNER JOIN auth_user auth ON log.created_by_id = auth.id
  INNER JOIN legalaid_case lc ON lc.id = log.case_id
  LEFT JOIN call_centre_operator op on op.user_id = log.created_by_id
  LEFT JOIN call_centre_organisation org ON org.id = op.organisation_id
WHERE
  log.code = 'CASE_VIEWED'
  AND log.created >= %(from_date)s
  AND log.created < %(to_date)s
  AND (%(case_reference)s IS NULL OR lc.reference = %(case_reference)s)
;
