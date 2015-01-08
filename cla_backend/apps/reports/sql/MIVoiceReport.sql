with
csvupload as (
select
  id
 ,created
 ,modified
 ,provider_id
 ,created_by_id
 ,json_array_elements(body) as body
 ,month
from cla_provider_csvupload)
select
  csv.id
  ,csv.created
  ,csv.modified
  ,csv.provider_id
  ,csv.created_by_id
  ,trim((csv.body->0)::text, '"') as "LAA_Reference"
  ,trim((csv.body->1)::text, '"') as "Client_Ref"
  ,trim((csv.body->2)::text, '"') as "Account_Number"
  ,trim((csv.body->3)::text, '"') as "First_Name"
  ,trim((csv.body->4)::text, '"') as "Surname"
  ,trim((csv.body->5)::text, '"') as "DOB"
  ,trim((csv.body->6)::text, '"') as "Age_Range"
  ,trim((csv.body->7)::text, '"') as "Gender"
  ,trim((csv.body->8)::text, '"') as "Ethnicity"
  ,trim((csv.body->11)::text, '"') as "Postcode"
  ,trim((csv.body->12)::text, '"') as "Eligibility_Code"
  ,trim((csv.body->13)::text, '"') as "Matter_Type_1"
  ,trim((csv.body->14)::text, '"') as "Matter_Type_2"
  ,trim((csv.body->15)::text, '"') as "Stage_Reached"
  ,trim((csv.body->16)::text, '"') as "Outcome_Code"
  ,trim((csv.body->18)::text, '"') as "Date_Opened"
  ,trim((csv.body->19)::text, '"') as "Date_Closed"
  ,trim((csv.body->20)::text, '"') as "Time_Spent"
  ,trim((csv.body->21)::text, '"') as "Case_Costs"
  ,trim((csv.body->23)::text, '"') as "Disability_Code"
  ,trim((csv.body->24)::text, '"') as "Disbursements"
  ,trim((csv.body->25)::text, '"') as "Travel_Costs"
  ,trim((csv.body->26)::text, '"') as "Determination"
  ,trim((csv.body->27)::text, '"') as "Suitable_For_Telephone_Advice"
  ,trim((csv.body->28)::text, '"') as "Exceptional_Case_ref"
  ,trim((csv.body->29)::text, '"') as "Exempted_Reason_Code"
  ,trim((csv.body->30)::text, '"') as "Adaptations"
  ,trim((csv.body->31)::text, '"') as "Signposting_or_Referral"
  ,trim((csv.body->32)::text, '"') as "Media_Code"
  ,trim((csv.body->33)::text, '"') as "Telephone_or_Online"
  ,csv.month
  ,p.name as "Provider"
  ,c.id::BOOL as "has_linked_case_in_system"
  ,c.billable_time as "OS_BillableTime"
  ,(
     SELECT count(t.id)
     FROM timer_timer t
       join cla_eventlog_log as tlog on t.id = tlog.timer_id
     WHERE t.linked_case_id = c.id
           and tlog.level >= 29
           and tlog.type='outcome'
           and tlog.code in ('IRKB', 'COSPF', 'NRES', 'DECL', 'NCTP', 'SPKB', 'SAME')
   ) as count_of_timers
  ,(
     SELECT count(log.id)
     FROM cla_eventlog_log log
     WHERE log.case_id = c.id
           and log.level >= 29
           and log.type='outcome'
           and log.code in ('IRKB', 'COSPF', 'NRES', 'DECL', 'NCTP', 'SPKB', 'SAME')
   ) as count_of_outcomes
from csvupload csv
  left JOIN cla_provider_provider p on csv.provider_id = p.id
  left outer join legalaid_case c on c.laa_reference::TEXT = trim((csv.body->0)::text, '"')::TEXT
WHERE csv.month = %s
;

