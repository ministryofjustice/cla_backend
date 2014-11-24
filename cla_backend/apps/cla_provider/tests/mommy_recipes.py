from model_mommy.recipe import Recipe, seq, foreign_key
from ..models import Provider, ProviderAllocation, OutOfHoursRota, Staff, \
    Feedback, CSVUpload


provider = Recipe(Provider,
    name=seq('Name'),
)

staff = Recipe(Staff)

outofhoursrota = Recipe(OutOfHoursRota)

provider_allocation = Recipe(ProviderAllocation)

feedback = Recipe(Feedback, created_by=foreign_key(staff))

csvupload_determination = Recipe(CSVUpload,
                   body=[
                       u'2222222', u'0000', u'1A111A', u'A', u'Corgi',
                       u'01/01/1901', u'D', u'F', u'1', u'', u'', u'SW1A 1AA',
                       u'', u'SWAG', u'YOLO', u'', u'', u'', u'', u'', u'18',
                       u'99.5', u'', u'MOB', u'', u'', u'AAAA', u'', u'', u'',
                       u'NAR', u'', u'', u'TA'
                   ]
)


csvupload_case = \
    Recipe(CSVUpload,
           body=[
               [
                   u'3333333', u'0001', u'2B222B', u'A N Other', u'Corgi',
                   u'02/01/1901', u'E', u'M', u'1', u'', u'', u'SW1A 1AA',
                   u'X', u'FFFF', u'QQQQ', u'QA', u'QM', u'', u'01/01/1901',
                   u'01/01/1902', u'99', u'99.5', u'', u'ILL', u'0', u'0', u'',
                   u'N', u'', u'', u'NAR', u'', u'DK', u'TA'
               ]
           ]
    )
