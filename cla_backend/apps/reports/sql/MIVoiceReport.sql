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
  c.id
  ,c.created
  ,c.modified
  ,c.provider_id
  ,c.created_by_id
  ,trim((c.body->0)::text, '"') as "LAA_Reference"
  ,trim((c.body->1)::text, '"') as "Client_Ref"
  ,trim((c.body->2)::text, '"') as "Account_Number"
  ,trim((c.body->3)::text, '"') as "First_Name"
  ,trim((c.body->4)::text, '"') as "Surname"
  ,trim((c.body->5)::text, '"') as "DOB"
  ,trim((c.body->6)::text, '"') as "Age_Range"
  ,trim((c.body->7)::text, '"') as "Gender"
  ,trim((c.body->8)::text, '"') as "Ethnicity"
  ,trim((c.body->11)::text, '"') as "Postcode"
  ,trim((c.body->12)::text, '"') as "Eligibility_Code"
  ,trim((c.body->13)::text, '"') as "Matter_Type_1"
  ,trim((c.body->14)::text, '"') as "Matter_Type_2"
  ,trim((c.body->15)::text, '"') as "Stage_Reached"
  ,trim((c.body->16)::text, '"') as "Outcome_Code"
  ,trim((c.body->18)::text, '"') as "Date_Opened"
  ,trim((c.body->19)::text, '"') as "Date_Closed"
  ,trim((c.body->20)::text, '"') as "Time_Spent"
  ,trim((c.body->21)::text, '"') as "Case_Costs"
  ,trim((c.body->23)::text, '"') as "Disability_Code"
  ,trim((c.body->24)::text, '"') as "Disbursements"
  ,trim((c.body->25)::text, '"') as "Travel_Costs"
  ,trim((c.body->26)::text, '"') as "Determination"
  ,trim((c.body->27)::text, '"') as "Suitable_For_Telephone_Advice"
  ,trim((c.body->28)::text, '"') as "Exceptional_Case_ref"
  ,trim((c.body->29)::text, '"') as "Exempted_Reason_Code"
  ,trim((c.body->30)::text, '"') as "Adaptations"
  ,trim((c.body->31)::text, '"') as "Signposting_or_Referral"
  ,trim((c.body->32)::text, '"') as "Media_Code"
  ,trim((c.body->33)::text, '"') as "Telephone_or_Online"

  ,c.month
from csvupload c;

