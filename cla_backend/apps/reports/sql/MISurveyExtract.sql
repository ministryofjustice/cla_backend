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
    (SELECT string_agg(method::varchar, ', ') FROM legalaid_contactresearchmethod AS contactresearchmethod INNER JOIN legalaid_personaldetails_contact_for_research_methods AS pd_contactresearchmethod ON pd_contactresearchmethod.contactresearchmethod_id = contactresearchmethod.id AND personaldetails_id = pd.id) AS "contact_for_research_via",
    safe_to_contact,
    (SELECT COUNT(legalaid_thirdpartydetails.id) > 0 FROM legalaid_thirdpartydetails WHERE legalaid_thirdpartydetails.personal_details_id=pd.id) AS "Third Party Contact",
    (SELECT string_agg(laa_reference::varchar, ', ') FROM legalaid_case c WHERE c.personal_details_id=pd.id),
    (SELECT string_agg(c.laa_reference::varchar, ', ') FROM legalaid_thirdpartydetails t RIGHT JOIN legalaid_case c ON c.thirdparty_details_id=t.id WHERE t.personal_details_id=pd.id),
    (SELECT cc_org.name as organisation FROM call_centre_organisation cc_org INNER JOIN legalaid_case c ON cc_org.id = c.organisation_id WHERE c.personal_details_id=pd.id) as "Organisation"
FROM
    legalaid_personaldetails AS pd
WHERE pd.contact_for_research = TRUE
    AND pd.safe_to_contact = 'SAFE'
    AND pd.created >= %s
    AND pd.created < %s
