SERVICE_ADAPTATIONS = {
    "CBI",
    "LLI",
    "BSL",
    "MIN",
    "TYP",
    "SWC",
    "OAD",
    "TPC",
    "TAF",
    "FRS",
    "NAR",
    "OTH",
    "MAR",
}

EXEMPTION_CODES = {"ECHI", "EDET", "EPRE"}

DISABILITY_INDICATOR = {
    "NCD",
    "MHC",
    "LDD",
    "ILL",
    "OTH",
    "UKN",
    "MOB",
    "DEA",
    "HEA",
    "VIS",
    "BLI",
    "PNS",
    "PHY",
    "SEN",
    "COG",
}

ADVICE_TYPES = {"TA", "OA", "FF"}

AGE_RANGE = {"A", "B", "C", "D", "E", "F", "G", "U"}

ELIGIBILITY_CODES = {"S", "T", "V", "W", "X", "Z"}

PREFIX_CATEGORY_LOOKUP = {
    "D": "debt",
    "W": "welfare",
    "H": "housing",
    "F": "family",
    "E": "education",
    "Q": "discrimination",
}

STAGE_REACHED_REQUIRED_MT1S = {
    "DMCA",
    "DMAP",
    "DIVB",
    "DORH",
    "DTOT",
    "QPRO",
    "QEMP",
    "QEQP",
    "QPRE",
    "QFUN",
    "QEDU",
    "QPUB",
    "QCON",
    "ESEN",
    "ENEG",
    "EXCE",
    "EDOT",
    "EADM",
    "EGTO",
    "EPRO",
    "EDDA",
    "EREO",
    "EEQU",
    "HRNT",
    "HPOT",
    "HANT",
    "HDIS",
    "HREP",
    "HHOM",
    "HULE",
    "HOOT",
    "HPPO",
    "HPWA",
    "HRAR",
    "HPOS",
}

STAGE_REACHED_NOT_ALLOWED_MT1S = {
    "WDLA",
    "WBAA",
    "WICB",
    "WSFP",
    "WHBT",
    "WIST",
    "WJSA",
    "WIIB",
    "WBBT",
    "WTAX",
    "WMUL",
    "WOTH",
    "WESA",
    "WBPI",
    "FAMA",
    "FAMB",
    "FAMC",
    "FAMD",
    "FAME",
    "FAMF",
    "FAMG",
    "FAMH",
    "FAMI",
    "FAMJ",
    "FAMK",
    "FAML",
    "FAMM",
    "FAMN",
    "FAMO",
    "FAMP",
    "FAMQ",
    "FAMR",
    "FAMS",
    "FAMV",
    "FAMW",
    "FAMX",
    "FAMY",
    "FAMZ",
    "FAM1",
    "FAM2",
    "FAM3",
}

POSTCODE_RE = r"""(?: # UK POSTCODE
    ( G[I1]R \s* [0O]AA | NFA | INT \s INT )           # special postcode
  |
    ( [A-PR-UWYZ01][A-Z01]? )       # area
    ( [0-9IO][0-9A-HJKMNPR-YIO]? )  # district
    (?: \s*
      ( [0-9IO] )                   # sector
      ( [ABD-HJLNPQ-Z10]{2} )       # unit
    )
)$"""
