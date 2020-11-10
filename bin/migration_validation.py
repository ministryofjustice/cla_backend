from __future__ import print_function
import sys
import os
import psycopg2


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_target_db_cursor():
    conn = psycopg2.connect(
        host=os.environ["TARGET_DB_HOST"],
        dbname=os.environ["TARGET_DB_NAME"],
        user=os.environ["TARGET_DB_USER"],
        password=os.environ["TARGET_DB_PASSWORD"],
    )

    return conn.cursor()


def get_source_db_cursor():
    conn = psycopg2.connect(
        host=os.environ["SOURCE_DB_HOST"],
        dbname=os.environ["SOURCE_DB_NAME"],
        user=os.environ["SOURCE_DB_USER"],
        password=os.environ["SOURCE_DB_PASSWORD"],
    )

    return conn.cursor()


def get_all_tables(cursor):
    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
    )

    return cursor.fetchall()


def get_row_count(cursor, table_name):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM %s
        """
        % table_name
    )
    return cursor.fetchone()[0]


def get_database_sequences(cursor):
    cursor.execute(
        """
        SELECT relname sequence_name
        FROM pg_class
        WHERE relkind = 'S'
        """
    )
    return cursor.fetchall()


def get_current_sequence_value(cursor, sequence):
    cursor.execute(
        """
        SELECT last_value
        FROM %s
        """
        % sequence
    )

    return cursor.fetchone()


def get_last_row(cursor, table_name):
    keys = {"django_session": "session_key"}
    cursor.execute(
        """
        SELECT *
        FROM %s
        ORDER BY %s desc
        LIMIT 1
        """
        % (table_name, keys.get(table_name, "id"))
    )
    return cursor.fetchone()


if __name__ == "__main__":
    target_cursor = get_target_db_cursor()
    source_cursor = get_source_db_cursor()
    target_tables = get_all_tables(target_cursor)
    source_tables = get_all_tables(source_cursor)

    errors = []
    for table in source_tables:
        # Check table exists in target database
        if table not in target_tables:
            errors.append("Table %s does not exist in target database" % table[0])
        else:
            # Check row count match for table
            source_count = get_row_count(source_cursor, table[0])
            target_count = get_row_count(target_cursor, table[0])
            if target_count != source_count:
                errors.append("Table {} \t source:{} target:{}".format(table[0], source_count, target_count))

            # Check last row match for table
            source_values = get_last_row(source_cursor, table[0])
            target_values = get_last_row(target_cursor, table[0])
            if source_values != target_values:
                errors.append("Target values in table %s do not match source" % table[0])

    source_sequences = get_database_sequences(source_cursor)
    target_sequences = get_database_sequences(target_cursor)
    for sequence in source_sequences:
        # Check sequence exists in database
        if sequence not in target_sequences:
            errors.append("Sequence %s does not exist in target database" % sequence[0])
        else:
            # Check last sequence values match
            source_sequence_value = get_current_sequence_value(source_cursor, sequence[0])
            target_sequence_value = get_current_sequence_value(target_cursor, sequence[0])
            if source_sequence_value != target_sequence_value:
                errors.append(
                    "Sequence {} \t source:{} target:{}".format(
                        sequence[0], source_sequence_value, target_sequence_value
                    )
                )

    if errors:
        eprint("\n".join(errors))
    else:
        print("Completed validation with no errors")
