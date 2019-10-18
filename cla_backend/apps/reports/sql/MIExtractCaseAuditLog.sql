SELECT c.reference as "Case", audit_log.action as "Action", audit_log.created::date AS "Date", auth.username as "Operator", org.name AS "Organisation", COUNT(audit_log.id) as "Count"
FROM cla_auditlog_auditlog audit_log
    INNER JOIN legalaid_case_audit_log case_log ON case_log.auditlog_id = audit_log.id
    INNER JOIN legalaid_case c ON case_log.case_id = c.id
    INNER JOIN auth_user auth ON audit_log.user_id = auth.id
    INNER JOIN call_centre_operator op on op.user_id = audit_log.user_id
    LEFT JOIN call_centre_organisation org ON org.id = op.organisation_id
GROUP BY auth.username, audit_log.created::date, c.reference, audit_log.action, org.name
ORDER BY audit_log.created::date DESC
