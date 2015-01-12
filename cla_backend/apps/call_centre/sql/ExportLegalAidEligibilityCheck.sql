COPY (SELECT
id,
created,
modified,
reference,
category_id,
you_id,
partner_id,
disputed_savings_id,
'[deleted]' AS your_problem_notes,
'[deleted]' AS notes,
state,
dependants_young,
dependants_old,
on_passported_benefits,
on_nass_benefits,
specific_benefits,
is_you_or_your_partner_over_60,
has_partner,
calculations
FROM legalaid_eligibilitycheck
WHERE modified >= %s::timestamp AND modified <= %s::timestamp)
TO '{path}/legalaid_eligibilitycheck.csv' CSV HEADER;
