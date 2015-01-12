COPY (SELECT
id,
created,
modified,
bank_balance,
investment_balance,
asset_balance,
credit_balance
FROM legalaid_savings
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/legalaid_savings.csv' CSV HEADER;
