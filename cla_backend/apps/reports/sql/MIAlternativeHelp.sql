WITH F2F as (

    SELECT
      log.id
      ,c.reference
      ,c.laa_reference
      ,category.code as "category"
      ,c.created as "created"
      ,log.code
      ,log.notes
      ,unnest(regexp_split_to_array(log.notes, '\n')) as f2f
    from
      cla_eventlog_log as log
      JOIN legalaid_case as c on c.id = log.case_id
      LEFT OUTER JOIN diagnosis_diagnosistraversal as diagnosis on c.diagnosis_id = diagnosis.id
      LEFT OUTER JOIN legalaid_category as category on diagnosis.category_id = category.id
    WHERE
      log.code = 'IRKB'
), NOTF2F as (
    SELECT
      log.id
      ,c.reference
      ,c.laa_reference
      ,category.code as "category"
      ,c.created as "created"
      ,log.code
      ,log.notes
      ,'EXTERNAL (http://http://find-legal-advice.justice.gov.uk/) see notes'::text as f2f
    from
      cla_eventlog_log as log
      JOIN legalaid_case as c on c.id = log.case_id
      LEFT OUTER JOIN diagnosis_diagnosistraversal as diagnosis on c.diagnosis_id = diagnosis.id
      LEFT OUTER JOIN legalaid_category as category on diagnosis.category_id = category.id
    WHERE
      log.code in ('COSPF', 'SPFN', 'SPFM')
), ALLREF as (

  SELECT f2f.*, kb.id as kb_id from F2F
    JOIN knowledgebase_article as kb on kb.service_name = f2f.f2f

  UNION ALL
  SELECT NOTF2F.*, null FROM NOTF2F

)
    SELECT * FROM ALLREF
    WHERE
      created >= %s
      and created < %s
    ORDER BY created desc
