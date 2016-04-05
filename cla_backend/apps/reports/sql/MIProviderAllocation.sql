SELECT * FROM
  crosstab(
    'SELECT
      cat.name      AS category,
      provider.name AS provider,
      COUNT(cse.id) AS num_allocations
    FROM legalaid_case cse
      INNER JOIN diagnosis_diagnosistraversal dt ON cse.diagnosis_id = dt.id
      JOIN cla_provider_provider provider ON cse.provider_id = provider.id
      JOIN legalaid_category cat ON cat.id = dt.category_id

    WHERE (cse.assigned_out_of_hours = FALSE AND
           NOT (cse.id IN (SELECT
                             U1.case_id AS case_id
                           FROM cla_eventlog_log U1
                           WHERE U1.code = ''MANREF'')) AND
          NOT (cse.provider_id IS NULL) AND
          cse.provider_assigned_at >= ''%s''::timestamp AND
          cse.provider_assigned_at <= ''%s''::timestamp)
    GROUP BY cat.name, provider.name, cat.id
    ORDER BY cat.id ASC'
    ,
    'SELECT name FROM cla_provider_provider ORDER BY id'
  ) AS (%s)
