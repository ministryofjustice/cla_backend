from extended_choices import Choices

LOG_LEVELS = Choices(
    # constant, db_id, friendly string
    # Indicates the importance of the event.
    # Events with level >= HIGH are denormalised on the
    # case as well and 'mark' the progress of a case
    # indirectly
    ('HIGH', 29, 'HIGH'),
    ('MODERATE', 21, 'MODERATE'),
    ('MINOR', 11, 'MINOR'),
)

LOG_TYPES = Choices(
    # constant, db_id, friendly string
    ('OUTCOME', 'outcome', 'outcome'),  # codes that CLA understands and uses. E.g. CLSP
    ('SYSTEM', 'system', 'system')  # system codes, somethimes shown to users as well. E.g. CASE_CREATED
)


LOG_ROLES = Choices(
    # constant, db_id, friendly string
    # Not currently used.
    ('OPERATOR', 'operator', 'operator'),
    ('SPECIALIST', 'specialist', 'special')
)
