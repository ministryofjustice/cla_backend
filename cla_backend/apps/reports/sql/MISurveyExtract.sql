SELECT
   md5(lower(regexp_replace((pd.full_name||pd.postcode)::text, '\s', '', 'ig'))) as "Hash_ID"
  ,created::timestamptz
  ,modified::timestamptz
  ,full_name
  ,postcode
  ,street
  ,mobile_phone as "phone"
  ,email
  ,date_of_birth
  ,ni_number
  ,contact_for_research
  ,safe_to_contact
from
   legalaid_personaldetails as pd
WHERE pd.contact_for_research = true
  and pd.safe_to_contact = 'SAFE'
  and pd.created >= %s
  and pd.created < %s
