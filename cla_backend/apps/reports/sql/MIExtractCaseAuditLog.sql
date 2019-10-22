SELECT c.reference, audit_log.action, auth.username, org.name, audit_log.created
FROM cla_auditlog_auditlog audit_log
    INNER JOIN legalaid_case_audit_log case_log ON case_log.auditlog_id = audit_log.id
    INNER JOIN legalaid_case c ON case_log.case_id = c.id
    INNER JOIN auth_user auth ON audit_log.user_id = auth.id
    INNER JOIN call_centre_operator op on op.user_id = audit_log.user_id
    LEFT JOIN call_centre_organisation org ON org.id = op.organisation_id
WHERE audit_log.created >= %(from_date)s AND audit_log.created < %(to_date)s
ORDER BY audit_log.created DESC
