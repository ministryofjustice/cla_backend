WITH complaint_logs AS (
    SELECT *
    FROM cla_eventlog_log
    WHERE cla_eventlog_log.content_type_id=(
        SELECT id
        FROM django_content_type
        WHERE django_content_type.app_label='complaints'
            AND django_content_type.model='complaint'
    )
    ORDER BY cla_eventlog_log.created DESC
)
SELECT
    c.laa_reference,
    c.reference,
    p.full_name,
    category.code,
    (SELECT CONCAT(auth_user.first_name, ' ', auth_user.last_name, ' (', auth_user.username, ')') FROM auth_user WHERE auth_user.id = comp.created_by_id) AS created_by,
    (SELECT CONCAT(auth_user.first_name, ' ', auth_user.last_name, ' (', auth_user.username, ')') FROM auth_user WHERE auth_user.id = comp.owner_id) AS owner,
    comp.source,
    comp.created,
    comp_cat.name,
    (SELECT complaint_logs.created FROM complaint_logs WHERE complaint_logs.object_id=comp.id AND complaint_logs.code='HOLDING_LETTER_SENT' LIMIT 1) AS holding_letter,
    (SELECT complaint_logs.created FROM complaint_logs WHERE complaint_logs.object_id=comp.id AND complaint_logs.code='FULL_RESPONSE_SENT' LIMIT 1) AS full_letter,
    CASE
        WHEN comp.level = %(major)s THEN 'Major'
        WHEN comp.level = %(minor)s THEN 'Minor'
        ELSE '(not specified)'
    END AS justified,
    CASE
        WHEN comp.justified IS NULL THEN ''
        WHEN comp.justified IS TRUE THEN 'Justified'
        WHEN comp.justified IS FALSE THEN 'Unjustified'
    END AS justified,
    (SELECT complaint_logs.created FROM complaint_logs WHERE complaint_logs.object_id=comp.id AND complaint_logs.code='COMPLAINT_CLOSED' LIMIT 1) AS closed,
    CASE
        WHEN comp.resolved IS NULL THEN ''
        WHEN comp.resolved IS TRUE THEN 'Resolved'
        WHEN comp.resolved IS FALSE THEN 'Unresolved'
    END AS resolved,
    (
        SELECT comp.created + INTERVAL %(sla_days)s > COALESCE(
            (SELECT complaint_logs.created FROM complaint_logs WHERE complaint_logs.object_id=comp.id AND complaint_logs.code='COMPLAINT_CLOSED' LIMIT 1),
            NOW()
        )
    ) AS within_sla,
    cc_org.name as organisation
FROM complaints_complaint AS comp
    LEFT OUTER JOIN complaints_category AS comp_cat ON comp_cat.id = comp.category_id
    JOIN legalaid_eoddetails AS eod ON comp.eod_id = eod.id
    JOIN legalaid_case AS c ON c.id = eod.case_id
    LEFT OUTER JOIN legalaid_personaldetails AS p ON p.id = c.personal_details_id
    LEFT OUTER JOIN diagnosis_diagnosistraversal AS diagnosis ON c.diagnosis_id = diagnosis.id
    LEFT OUTER JOIN legalaid_category AS category ON diagnosis.category_id = category.id
    LEFT OUTER JOIN call_centre_organisation AS cc_org ON cc_org.id = c.organisation_id
WHERE comp.created >= %(from_date)s AND comp.created < %(to_date)s AND
(SELECT COUNT(id) FROM complaint_logs WHERE complaint_logs.object_id=comp.id AND complaint_logs.code = 'COMPLAINT_VOID') = 0
ORDER BY comp.created DESC;
