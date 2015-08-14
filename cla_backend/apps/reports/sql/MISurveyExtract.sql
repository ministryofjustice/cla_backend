SELECT
    md5(lower(regexp_replace((pd.full_name || pd.postcode) :: TEXT, '\s+', '', 'ig'))) AS "Hash_ID",
    created :: TIMESTAMPTZ,
    modified :: TIMESTAMPTZ,
    full_name,
    postcode,
    street,
    mobile_phone AS "phone",
    email,
    date_of_birth,
    ni_number,
    contact_for_research,
    safe_to_contact,
    (SELECT COUNT(legalaid_thirdpartydetails.id) > 0 FROM legalaid_thirdpartydetails WHERE legalaid_thirdpartydetails.personal_details_id=pd.id) AS "Third Party Contact"
FROM
    legalaid_personaldetails AS pd
WHERE pd.contact_for_research = TRUE
    AND pd.safe_to_contact = 'SAFE'
    AND pd.created >= %s
    AND pd.created < %s
