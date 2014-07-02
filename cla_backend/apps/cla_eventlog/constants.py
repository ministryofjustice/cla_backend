from extended_choices import Choices

LOG_LEVELS = Choices(
    # constant, db_id, friendly string
    ('HIGH', 29, 'HIGH'),
    ('MODERATE', 21, 'MODERATE'),
    ('MINOR', 11, 'MINOR'),
)

LOG_TYPES = Choices(
    # constant, db_id, friendly string
    ('OUTCOME', 'outcome', 'outcome'),
    ('SYSTEM', 'system', 'system')
)


LOG_ROLES = Choices(
    # constant, db_id, friendly string
    ('OPERATOR', 'operator', 'operator'),
    ('SPECIALIST', 'specialist', 'special')
)