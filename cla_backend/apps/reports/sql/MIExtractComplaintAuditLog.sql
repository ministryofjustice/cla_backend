SELECT c.reference, complaint_log.complaint_id, audit_log.action, auth.username, org.name, audit_log.created
FROM cla_auditlog_auditlog audit_log
    INNER JOIN complaints_complaint_audit_log complaint_log ON audit_log.id = complaint_log.auditlog_id
	INNER JOIN complaints_complaint complaint ON complaint.id = complaint_log.complaint_id
	INNER JOIN legalaid_eoddetails eod ON eod.id = complaint.eod_id
    INNER JOIN legalaid_case c ON c.id = eod.case_id
    INNER JOIN auth_user auth ON auth.id = audit_log.user_id
    INNER JOIN call_centre_operator op on op.user_id = audit_log.user_id
    LEFT JOIN call_centre_organisation org ON org.id = op.organisation_id
WHERE audit_log.created >= %(from_date)s AND audit_log.created < %(to_date)s
ORDER BY audit_log.created DESC
