import itertools
from copy import copy, deepcopy
from datetime import datetime

from django.conf import settings

CONTRACT_THIRTEEN = "2013"
CONTRACT_EIGHTEEN = "2018"
CONTRACT_EIGHTEEN_DISCRIMINATION = "2018-discrimination"
CONTRACT_THIRTEEN_START_DATE = datetime(year=2013, month=4, day=1)
CONTRACT_THIRTEEN_END_DATE = datetime(year=2018, month=9, day=1)
CONTRACT_EIGHTEEN_START_DATE = CONTRACT_THIRTEEN_END_DATE

contract_2013_determination_codes = {u"OOSC", u"OSPF", u"CHNM", u"FINI", u"DVCA"}
contract_2018_determination_codes = copy(contract_2013_determination_codes) | {"FAFA", "EXEM"}
contract_2018_fixed_fee_codes = {u"DF", u"HF", u"LF", u"MR", u"HM", u"NA"}

debt_category_spec = {
    "OUTCOME_CODES": {u"DA", u"DC", u"DD", u"DG", u"DH", u"DI", u"DU", u"DV", u"DW", u"DX", u"DY", u"DZ"},
    "MATTER_TYPE1": {u"DPDE", u"DNPD", u"DMDE", u"DMCA", u"DMAP", u"DIVB", u"DORH", u"DTOT"},
    "MATTER_TYPE2": {u"DVAL", u"DMIX", u"DCRE", u"DIBP", u"DORD", u"DOTH", u"DSCH"},
    "STAGE_REACHED": {u"DA", u"DB", u"DC", u"DD"},
}
discrimination_category_spec = {
    "OUTCOME_CODES": {
        u"QA",
        u"QB",
        u"QC",
        u"QD",
        u"QE",
        u"QF",
        u"QG",
        u"QH",
        u"QI",
        u"QJ",
        u"QK",
        u"QL",
        u"QM",
        u"QT",
        u"QU",
        u"QV",
        u"QW",
        u"QX",
        u"QY",
        u"QZ",
    },
    "MATTER_TYPE1": {u"QPRO", u"QEMP", u"QEQP", u"QPRE", u"QFUN", u"QEDU", u"QPUB", u"QCON"},
    "MATTER_TYPE2": {u"QAGE", u"QDIS", u"QGEN", u"QMCP", u"QPRM", u"QRAC", u"QROB", u"QSEX", u"QSOR", u"QMDI"},
    "STAGE_REACHED": {u"QA", u"QB", u"QC", u"QD", u"QE", u"QF", u"QG", u"QH"},
}
education_category_spec = {
    "OUTCOME_CODES": {
        u"EA",
        u"EB",
        u"EC",
        u"ED",
        u"EE",
        u"EF",
        u"EG",
        u"EH",
        u"EI",
        u"EJ",
        u"EK",
        u"EU",
        u"EV",
        u"EW",
        u"EX",
        u"EY",
        u"EZ",
    },
    "MATTER_TYPE1": {u"ESEN", u"ENEG", u"EXCE", u"EDOT", u"EADM", u"EGTO", u"EPRO", u"EDDA", u"EREO", u"EEQU"},
    "MATTER_TYPE2": {
        u"ENUR",
        u"EDSC",
        u"EPRU",
        u"ECOL",
        u"EUNI",
        u"EAAP",
        u"ELOC",
        u"EIAP",
        u"ESOS",
        u"EHEF",
        u"EOTH",
    },
    "STAGE_REACHED": {u"EA", u"EB", u"EC", u"ED"},
}
family_category_spec = {
    "OUTCOME_CODES": {
        u"FA",
        u"FB",
        u"FC",
        u"FD",
        u"FE",
        u"FF",
        u"FG",
        u"FH",
        u"FI",
        u"FJ",
        u"FT",
        u"FU",
        u"FV",
        u"FW",
        u"FX",
        u"FY",
        u"FZ",
        u"FS",
    },
    "MATTER_TYPE1": {
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
        u"FAMT",
        u"FAMU",
        u"FAMV",
        u"FAMW",
        u"FAMX",
        u"FAMY",
        u"FAMZ",
        u"FAM1",
        u"FAM2",
        u"FAM3",
    },
    "MATTER_TYPE2": {
        u"FADV",
        u"FPET",
        u"FRES",
        u"FAPP",
        u"FREP",
        u"FCHG",
        u"FCHS",
        u"FOTH",
        u"FMEC",
        u"FMEF",
        u"FMEA",
    },
    "STAGE_REACHED": {u"FA", u"FB", u"FC", u"FD"},
}
housing_category_spec = {
    "OUTCOME_CODES": {
        u"HA",
        u"HD",
        u"HE",
        u"HF",
        u"HG",
        u"HH",
        u"HI",
        u"HJ",
        u"HK",
        u"HL",
        u"HM",
        u"HU",
        u"HV",
        u"HW",
        u"HX",
        u"HY",
        u"HZ",
    },
    "MATTER_TYPE1": {
        u"HRNT",
        u"HMOR",
        u"HPOT",
        u"HANT",
        u"HDIS",
        u"HREP",
        u"HREH",
        u"HHOM",
        u"HBFT",
        u"HULE",
        u"HLAN",
        u"HOOT",
    },
    "MATTER_TYPE2": {u"HPUB", u"HPRI", u"HHAC", u"HNAS", u"HOWN", u"HHLS", u"HLAN", u"HOTH"},
    "STAGE_REACHED": {u"HA", u"HB", u"HC", u"HD"},
}
welfare_category_spec = {
    "OUTCOME_CODES": {u"WA", u"WB", u"WC", u"WD", u"WE", u"WG", u"WU", u"WV", u"WZ"},
    "MATTER_TYPE1": {
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
        u"WBUC",
    },
    "MATTER_TYPE2": {
        u"WREA",
        u"WREV",
        u"WSSC",
        u"WAPL",
        u"WOVE",
        u"WBAC",
        u"WLGO",
        u"WOTH",
        u"WNAS",
        u"WBPA",
        u"WBUT",
        u"WBCA",
        u"WBSC",
        u"WBHC",
    },
    "STAGE_REACHED": {u"WA", u"WB", u"WC", u"WD"},
}

contract_2013_category_spec = {
    u"debt": deepcopy(debt_category_spec),
    u"discrimination": deepcopy(discrimination_category_spec),
    u"education": deepcopy(education_category_spec),
    u"family": deepcopy(family_category_spec),
    u"housing": deepcopy(housing_category_spec),
    u"welfare": deepcopy(welfare_category_spec),
}

# TODO Implement contract 2018 changes here
discrimination_category_spec["OUTCOME_CODES"].update({u"QAA"})
family_category_spec["OUTCOME_CODES"].update({u"FAA", u"FAB", u"FAC"})
housing_category_spec["OUTCOME_CODES"].update({u"HAA", u"HAC", "HAB"})

contract_2018_category_spec = {
    u"debt": deepcopy(debt_category_spec),
    u"discrimination": deepcopy(discrimination_category_spec),
    u"education": deepcopy(education_category_spec),
    u"family": deepcopy(family_category_spec),
    u"housing": deepcopy(housing_category_spec),
    u"welfare": deepcopy(welfare_category_spec),
}

contract_2018_category_spec["family"]["OUTCOME_CODES"].update({u"DAA"})


def get_all_values_across_categories(key, applicable_contract):
    category_spec = contract_2013_category_spec
    if applicable_contract == CONTRACT_EIGHTEEN:
        category_spec = contract_2018_category_spec
    return list(itertools.chain.from_iterable([spec[key] for _, spec in category_spec.items()]))


def get_valid_outcomes(applicable_contract):
    return get_all_values_across_categories("OUTCOME_CODES", applicable_contract)


def get_valid_stage_reached(applicable_contract):
    return get_all_values_across_categories("STAGE_REACHED", applicable_contract)


def get_valid_matter_type1(applicable_contract):
    return get_all_values_across_categories("MATTER_TYPE1", applicable_contract)


def get_valid_matter_type2(applicable_contract):
    return get_all_values_across_categories("MATTER_TYPE2", applicable_contract)


def get_determination_codes(applicable_contract):
    if applicable_contract == CONTRACT_EIGHTEEN:
        return contract_2018_determination_codes
    return contract_2013_determination_codes


def get_applicable_contract(case_date_opened, case_matter_type_1=None):
    if not settings.CONTRACT_2018_ENABLED:
        return CONTRACT_THIRTEEN
    try:
        if CONTRACT_THIRTEEN_START_DATE <= case_date_opened < CONTRACT_THIRTEEN_END_DATE:
            return CONTRACT_THIRTEEN
        elif case_date_opened >= CONTRACT_EIGHTEEN_START_DATE:
            if case_matter_type_1 in contract_2018_category_spec["discrimination"]["MATTER_TYPE1"]:
                return CONTRACT_EIGHTEEN_DISCRIMINATION
            return CONTRACT_EIGHTEEN
    except TypeError:
        return CONTRACT_THIRTEEN
