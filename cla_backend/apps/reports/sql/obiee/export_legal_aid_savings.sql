COPY (SELECT
id,
created,
modified,
bank_balance,
investment_balance,
asset_balance,
credit_balance
FROM legalaid_savings
WHERE (modified >= %(from_date)s::timestamp AND modified <= %(to_date)s::timestamp)
OR (created >= %(from_date)s::timestamp AND created <= %(to_date)s::timestamp))
TO STDOUT CSV HEADER;
