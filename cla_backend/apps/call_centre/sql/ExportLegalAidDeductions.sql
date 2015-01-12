COPY (SELECT
id,
created,
modified,
income_tax_interval_period,
income_tax_per_interval_value,
income_tax,
national_insurance_interval_period,
national_insurance_per_interval_value,
national_insurance,
maintenance_interval_period,
maintenance_per_interval_value,
maintenance,
childcare_interval_period,
childcare_per_interval_value,
childcare,
mortgage_interval_period,
mortgage_per_interval_value,
mortgage,
rent_interval_period,
rent_per_interval_value,
rent,
criminal_legalaid_contributions
FROM legalaid_deductions
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/legalaid_deductions.csv' CSV HEADER;
