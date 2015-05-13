WITH
  report_dates AS (
    SELECT day, 0 as blank_count FROM
      generate_series('2015-04-01 00:00'::timestamp, '2015-04-30 00:00'::timestamp, '1 day')
        AS day
  ), report_cases AS (
    SELECT
      id,
      date_trunc('day', created) AS day 
    FROM legalaid_case 
    WHERE created >= '2015-04-01 00:00'::timestamp AND created <= '2015-04-30 00:00'::timestamp
    GROUP BY date_trunc('day', created), legalaid_case.id
  ), diagnosis AS (
    SELECT
      id,
      state,
      date_trunc('day', created) AS day
    FROM diagnosis_diagnosistraversal
    WHERE created >= '2015-04-01 00:00'::timestamp AND created <= '2015-04-30 00:00'::timestamp
    GROUP BY date_trunc('day', created), diagnosis_diagnosistraversal.id
  )
SELECT
  report_dates.day as "Date",
  COUNT(diagnosis.id) as "Diagnosis",
  (SELECT COUNT(*) FROM diagnosis WHERE state = 'UNKNOWN' AND diagnosis.day = report_dates.day) as "Scope_unknown",
  (SELECT COUNT(*) FROM diagnosis WHERE state = 'OUTOFSCOPE' AND diagnosis.day = report_dates.day) as "Outofscope",
  (SELECT COUNT(*) FROM diagnosis WHERE state = 'CONTACT' AND diagnosis.day = report_dates.day) as "Scope_contact",
  (SELECT COUNT(*) FROM diagnosis WHERE state = 'INSCOPE' AND diagnosis.day = report_dates.day) as "Inscope",
  COUNT(report_cases.id) as "Cases"
FROM report_dates
LEFT OUTER JOIN report_cases ON report_cases.day = report_dates.day
LEFT OUTER JOIN diagnosis ON diagnosis.day = report_dates.day
GROUP BY report_dates.day
ORDER BY report_dates.day;