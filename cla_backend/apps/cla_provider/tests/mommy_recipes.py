from model_mommy.recipe import Recipe, seq, foreign_key
from ..models import Provider, ProviderAllocation, OutOfHoursRota, Staff, Feedback, CSVUpload, WorkingDays

provider = Recipe(Provider, name=seq("Name"))
staff = Recipe(Staff)

outofhoursrota = Recipe(OutOfHoursRota)

provider_allocation = Recipe(ProviderAllocation)

working_days = Recipe(WorkingDays)

feedback = Recipe(Feedback, created_by=foreign_key(staff))

csvupload_determination = Recipe(
    CSVUpload,
    body=[
        "2222222",
        "0000",
        "1A111A",
        "A",
        "Corgi",
        "01/01/1901",
        "D",
        "F",
        "1",
        "",
        "",
        "SW1A 1AA",
        "",
        "SWAG",
        "YOLO",
        "",
        "",
        "",
        "",
        "",
        "18",
        "99.5",
        "",
        "MOB",
        "",
        "",
        "AAAA",
        "",
        "",
        "",
        "NAR",
        "",
        "",
        "TA",
    ],
)

csvupload_case = Recipe(
    CSVUpload,
    body=[
        [
            "3333333",
            "0001",
            "2B222B",
            "A N Other",
            "Corgi",
            "02/01/1901",
            "E",
            "M",
            "1",
            "",
            "",
            "SW1A 1AA",
            "X",
            "FFFF",
            "QQQQ",
            "QA",
            "QM",
            "",
            "01/01/1901",
            "01/01/1902",
            "99",
            "99.5",
            "",
            "ILL",
            "0",
            "0",
            "",
            "N",
            "",
            "",
            "NAR",
            "",
            "DK",
            "TA",
        ]
    ],
)
