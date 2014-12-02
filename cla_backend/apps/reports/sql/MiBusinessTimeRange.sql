CREATE OR REPLACE FUNCTION non_business_seconds_between(start timestamptz , finish timestamptz)
  RETURNS int AS $$
DECLARE seconds int;
BEGIN
WITH is_business_hours_series AS
(SELECT
  s
   ,CASE
    when EXTRACT(HOUR from s at time zone 'Europe/London') >= 18 or (EXTRACT(HOUR from s at time zone 'Europe/London') = 17 and EXTRACT(MINUTE from s at time zone 'Europe/London') >= 30 ) then true -- after 17:30
    when EXTRACT(HOUR from s at time zone 'Europe/London') < 9 then true -- before 9
    when EXTRACT(DOW from s at time zone 'Europe/London') in (6,0)  then true -- weekend
    ELSE false
    END as is_out_of_hours
FROM  generate_series(start, finish, '1 second'::interval) as s
)
   SELECT
    count(s) into seconds
   FROM is_business_hours_series
  where is_out_of_hours = false;
  RETURN seconds;
END;
$$
  LANGUAGE plpgsql
  IMMUTABLE;


