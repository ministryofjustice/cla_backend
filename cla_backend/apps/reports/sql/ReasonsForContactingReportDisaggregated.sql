select cr.id as rfc_id, lc.id as case_id, (case when lc.outcome_code = '' then 'I will call CLA back'  
when lc.thirdparty_details_id > 0 then 'Call someone else instead of me' when lc.outcome_code like 'CB1' 
then 'Call me back' else 'Not submitted' end), string_agg(cr2.category, ', ') as contact_reason,
le.notes as problem_notes, la.bsl_webcam, la.minicom, la.text_relay, la.skype_webcam, 
la."language", la.notes as other_comm_notes, cr.created as contact_date
from legalaid_case lc 
left join legalaid_eligibilitycheck le on lc.eligibility_check_id = le.id 
left join legalaid_adaptationdetails la on lc.adaptation_details_id = la.id
full join checker_reasonforcontacting cr on lc.id = cr.case_id
full join checker_reasonforcontactingcategory cr2 on cr2.reason_for_contacting_id = cr.id
where cr2.reason_for_contacting_id is not null and cr.created >= %(from_date)s and cr.created < %(to_date)s
group by cr.id, lc.id, cr.created, le.notes, la.bsl_webcam,
la.minicom, la.text_relay, la.skype_webcam, la."language", la.notes
ORDER BY cr.created desc
