SERVICE_ADAPTATIONS = {
    u"CBI",
    u"LLI",
    u"BSL",
    u"MIN",
    u"TYP",
    u"SWC",
    u"OAD",
    u"TPC",
    u"TAF",
    u"FRS",
    u"NAR",
    u"OTH",
    u"MAR",
}

EXEMPTION_CODES = {u"ECHI", u"EDET", u"EPRE"}

DISABILITY_INDICATOR = {
    u"NCD",
    u"MHC",
    u"LDD",
    u"ILL",
    u"OTH",
    u"UKN",
    u"MOB",
    u"DEA",
    u"HEA",
    u"VIS",
    u"BLI",
    u"PNS",
    u"PHY",
    u"SEN",
    u"COG",
}

ADVICE_TYPES = {u"TA", u"OA", u"FF"}

AGE_RANGE = {u"A", u"B", u"C", u"D", u"E", u"F", u"G", u"U"}

ELIGIBILITY_CODES = {u"S", u"T", u"V", u"W", u"X", u"Z"}

PREFIX_CATEGORY_LOOKUP = {
    u"D": u"debt",
    u"W": u"welfare",
    u"H": u"housing",
    u"F": u"family",
    u"E": u"education",
    u"Q": u"discrimination",
}

STAGE_REACHED_REQUIRED_MT1S = {
    u"DMCA",
    u"DMAP",
    u"DIVB",
    u"DORH",
    u"DTOT",
    u"QPRO",
    u"QEMP",
    u"QEQP",
    u"QPRE",
    u"QFUN",
    u"QEDU",
    u"QPUB",
    u"QCON",
    u"ESEN",
    u"ENEG",
    u"EXCE",
    u"EDOT",
    u"EADM",
    u"EGTO",
    u"EPRO",
    u"EDDA",
    u"EREO",
    u"EEQU",
    u"HRNT",
    u"HPOT",
    u"HANT",
    u"HDIS",
    u"HREP",
    u"HHOM",
    u"HULE",
    u"HOOT",
    u"HPPO",
    u"HPWA",
    u"HRAR",
    u"HPOS",
}

STAGE_REACHED_NOT_ALLOWED_MT1S = {
    u"WDLA",
    u"WBAA",
    u"WICB",
    u"WSFP",
    u"WHBT",
    u"WIST",
    u"WJSA",
    u"WIIB",
    u"WBBT",
    u"WTAX",
    u"WMUL",
    u"WOTH",
    u"WESA",
    u"WBPI",
    u"FAMA",
    u"FAMB",
    u"FAMC",
    u"FAMD",
    u"FAME",
    u"FAMF",
    u"FAMG",
    u"FAMH",
    u"FAMI",
    u"FAMJ",
    u"FAMK",
    u"FAML",
    u"FAMM",
    u"FAMN",
    u"FAMO",
    u"FAMP",
    u"FAMQ",
    u"FAMR",
    u"FAMS",
    u"FAMV",
    u"FAMW",
    u"FAMX",
    u"FAMY",
    u"FAMZ",
    u"FAM1",
    u"FAM2",
    u"FAM3",
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
