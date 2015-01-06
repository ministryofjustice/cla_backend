CREATE OR REPLACE FUNCTION cla_db_to_csv(dt_from TEXT, dt_to TEXT, path TEXT) RETURNS void AS $$
declare
  tables RECORD;
  statement TEXT;
begin
  FOR tables IN 
    SELECT (table_schema || '.' || table_name) AS schema_table
    FROM information_schema.tables t INNER JOIN information_schema.schemata s 
    ON s.schema_name = t.table_schema 
    WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema', 'configuration') 
      AND t.table_name NOT IN ('legalaid_personaldetails', 'legalaid_case', 'auth_group',
        'auth_group_permissions', 'auth_permission', 'auth_user_groups', 
        'auth_user_user_permissions', 'auth_user', 'django_admin_log', 
        'django_content_type', 'django_migrations', 'django_session', 'django_site',
        'oauth2_accesstoken', 'oauth2_client', 'oauth2_grant', 
        'oauth2_refreshtoken', 'south_migrationhistory',
        'legalaid_mediacodegroup')
    ORDER BY schema_table
  LOOP
    statement := 'COPY (SELECT * FROM ' || tables.schema_table || 
      ' WHERE created >= ''' || dt_from || '''::timestamp AND created <= ''' ||
      dt_to || '''::timestamp) TO ''' || path || '/' || tables.schema_table || 
      '.csv' ||''' CSV HEADER';
    EXECUTE statement;
  END LOOP;
  return;  
end;
$$ LANGUAGE plpgsql;

SELECT cla_db_to_csv(%s, %s, '{path}');
