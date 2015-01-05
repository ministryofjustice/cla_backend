COPY (SELECT id
,created
,modified
,reference
,eligibility_check_id
,personal_details_id
,created_by_id
,locked_by_id
,locked_at
,provider_id
,'[deleted]' AS notes
,provider_notes
,laa_reference
,thirdparty_details_id
,adaptation_details_id
,billable_time
,matter_type1_id
,matter_type2_id
,requires_action_by
,media_code_id
,diagnosis_id
,outcome_code
,level
,exempt_user
,exempt_user_reason
,ecf_statement
,outcome_code_id
,from_case_id
,provider_viewed
,requires_action_at
,callback_attempt
,source
,provider_closed
,provider_accepted
FROM legalaid_case
WHERE created >= %s::timestamp AND created <= %s::timestamp)
TO '{path}/public.legalaid_case.csv' CSV HEADER;
