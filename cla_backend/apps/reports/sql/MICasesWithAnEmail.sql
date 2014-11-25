SELECT
  count(c.id)
FROM legalaid_case c
  join legalaid_personaldetails p on p.id = c.personal_details_id
WHERE
  p.email is not null and p.email != ''
