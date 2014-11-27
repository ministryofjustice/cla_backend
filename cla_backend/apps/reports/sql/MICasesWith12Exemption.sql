SELECT
  count(c.id), c.exempt_user, c.exempt_user_reason
FROM legalaid_case c
  WHERE
  c.exempt_user
group by c.exempt_user, c.exempt_user_reason
