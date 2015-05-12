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
  )
SELECT
  report_dates.day,
  COUNT(report_cases.id)
FROM report_dates
LEFT OUTER JOIN report_cases ON report_cases.day = report_dates.day
GROUP BY report_dates.day
ORDER BY report_dates.day;