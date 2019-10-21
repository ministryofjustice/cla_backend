SELECT c.reference as "Case", audit_log.action as "Action", audit_log.created::date AS "Date", auth.username as "Operator", org.name AS "Organisation", COUNT(audit_log.id) as "Count"
FROM cla_auditlog_auditlog audit_log
    INNER JOIN complaints_complaint_audit_log complaint_log ON audit_log.id = complaint_log.auditlog_id
	INNER JOIN complaints_complaint complaint ON complaint.id = complaint_log.complaint_id
	INNER JOIN legalaid_eoddetails eod ON eod.id = complaint.eod_id
    INNER JOIN legalaid_case c ON c.id = eod.case_id
    INNER JOIN auth_user auth ON auth.id = audit_log.user_id
    INNER JOIN call_centre_operator op on op.user_id = audit_log.user_id
    LEFT JOIN call_centre_organisation org ON org.id = op.organisation_id
GROUP BY auth.username, audit_log.created::date, c.reference, audit_log.action, org.name
ORDER BY audit_log.created::date
