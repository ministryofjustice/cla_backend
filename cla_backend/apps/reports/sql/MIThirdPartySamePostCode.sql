SELECT
  count(c.id)
FROM legalaid_case c
  join legalaid_personaldetails p on p.id = c.personal_details_id
  join legalaid_thirdpartydetails t on t.id = c.thirdparty_details_id
  join legalaid_personaldetails tp on t.personal_details_id = tp.id
WHERE
  tp.postcode = p.postcode
