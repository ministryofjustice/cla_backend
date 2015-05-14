WITH
  report_dates AS (
    SELECT day, 0 as blank_count FROM
      generate_series(%(from_date)s::timestamp, %(to_date)s::timestamp, '1 day')
        AS day
  ), report_cases AS (
    SELECT
      lc.id as id,
      date_trunc('day', lc.created) AS day,
      le.state as state,
      lc.billable_time as billable_time,
      lc.source as source
    FROM legalaid_case lc
    LEFT OUTER JOIN legalaid_eligibilitycheck le ON le.id = lc.eligibility_check_id
    WHERE lc.created >= %(from_date)s::timestamp AND lc.created <= %(to_date)s::timestamp
    GROUP BY date_trunc('day', lc.created), lc.id, le.state, lc.source
  ), diagnosis AS (
    SELECT
      id,
      state,
      date_trunc('day', created) AS day
    FROM diagnosis_diagnosistraversal
    WHERE created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp
    GROUP BY date_trunc('day', created), diagnosis_diagnosistraversal.id
  ), eligibility_check AS (
    SELECT
      id,
      state,
      date_trunc('day', created) AS day
    FROM legalaid_eligibilitycheck
    WHERE created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp
    GROUP BY date_trunc('day', created), legalaid_eligibilitycheck.id
  )
SELECT
  report_dates.day as "Date",
  (SELECT COUNT(*) FROM diagnosis WHERE diagnosis.day = report_dates.day) as "Diagnosis_total",
  (SELECT COUNT(*) FROM diagnosis WHERE state = 'UNKNOWN' AND diagnosis.day = report_dates.day) as "Scope_unknown",
  (SELECT COUNT(*) FROM diagnosis WHERE state = 'OUTOFSCOPE' AND diagnosis.day = report_dates.day) as "Outofscope",
  (SELECT COUNT(*) FROM diagnosis WHERE state = 'CONTACT' AND diagnosis.day = report_dates.day) as "Scope_contact",
  (SELECT COUNT(*) FROM diagnosis WHERE state = 'INSCOPE' AND diagnosis.day = report_dates.day) as "Inscope",
  
  (SELECT COUNT(*) FROM eligibility_check WHERE eligibility_check.day = report_dates.day) as "Eligibility_check_total",
  (SELECT COUNT(*) FROM eligibility_check WHERE state = 'unknown' AND eligibility_check.day = report_dates.day) as "Eligibility_check_unknown",
  (SELECT COUNT(*) FROM eligibility_check WHERE state = 'no' AND eligibility_check.day = report_dates.day) as "Eligibility_check_ineligible",
  (SELECT COUNT(*) FROM eligibility_check WHERE state = 'yes' AND eligibility_check.day = report_dates.day) as "Eligibility_check_eligible",
  
  (SELECT COUNT(*) FROM report_cases WHERE report_cases.day = report_dates.day) as "Cases_total",
  (SELECT COUNT(*) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.state = 'unknown') as "Cases_unknown",
  (SELECT COUNT(*) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.state = 'no') as "Cases_ineligible",
  (SELECT COUNT(*) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.state = 'yes') as "Cases_eligible",

  (SELECT COALESCE(SUM(report_cases.billable_time), 0) FROM report_cases WHERE report_cases.day = report_dates.day) as "Time_total",
  (SELECT COALESCE(SUM(report_cases.billable_time), 0) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.state = 'unknown') as "Time_unknown",
  (SELECT COALESCE(SUM(report_cases.billable_time), 0) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.state = 'no') as "Time_ineligible",
  (SELECT COALESCE(SUM(report_cases.billable_time), 0) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.state = 'yes') as "Time_eligible",

  (SELECT COALESCE(SUM(report_cases.billable_time), 0) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.source = 'WEB') as "Time_web_total",
  (SELECT COALESCE(SUM(report_cases.billable_time), 0) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.state = 'unknown'AND report_cases.source = 'WEB') as "Time_web_unknown",
  (SELECT COALESCE(SUM(report_cases.billable_time), 0) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.state = 'no'AND report_cases.source = 'WEB') as "Time_web_ineligible",
  (SELECT COALESCE(SUM(report_cases.billable_time), 0) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.state = 'yes'AND report_cases.source = 'WEB') as "Time_web_eligible",

  (SELECT COALESCE(SUM(report_cases.billable_time), 0) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.source = 'PHONE') as "Time_phone_total",
  (SELECT COALESCE(SUM(report_cases.billable_time), 0) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.state = 'unknown' AND report_cases.source = 'PHONE') as "Time_phone_unknown",
  (SELECT COALESCE(SUM(report_cases.billable_time), 0) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.state = 'no' AND report_cases.source = 'PHONE') as "Time_phone_ineligible",
  (SELECT COALESCE(SUM(report_cases.billable_time), 0) FROM report_cases WHERE report_cases.day = report_dates.day AND report_cases.state = 'yes' AND report_cases.source = 'PHONE') as "Time_phone_eligible"
FROM report_dates
GROUP BY report_dates.day
ORDER BY report_dates.day;