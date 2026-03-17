import itertools
from copy import copy, deepcopy
from datetime import datetime

from django.conf import settings

CONTRACT_THIRTEEN = "2013"
CONTRACT_EIGHTEEN = "2018"
CONTRACT_EIGHTEEN_DISCRIMINATION = "2018-discrimination"
CONTRACT_EIGHTEEN_EDUCATION = "2018-education"
CONTRACT_THIRTEEN_START_DATE = datetime(year=2013, month=4, day=1)
CONTRACT_THIRTEEN_END_DATE = datetime(year=2018, month=9, day=1)
CONTRACT_EIGHTEEN_START_DATE = CONTRACT_THIRTEEN_END_DATE

contract_2013_determination_codes = {"OOSC", "OSPF", "CHNM", "FINI", "DVCA"}
contract_2018_determination_codes = copy(contract_2013_determination_codes) | {"FAFA", "EXEM"}
contract_2018_signposting_codes = {"OOSC", "TANA", "OSPF", "CHNM", "FINI", "FREP", "LREP"}
contract_2018_fixed_fee_codes = {"DF", "HF", "LF", "MR", "HM", "NA", "HR"}

contact_2018_outcome_codes_requiring_signposting_code = {
    "DU",
    "DV",
    "DW",
    "QU",
    "QV",
    "QW",
    "EU",
    "EV",
    "EW",
    "FU",
    "FV",
    "FW",
    "FX",
    "FY",
    "FZ",
    "HU",
    "HV",
    "HW",
    "WU",
    "WV",
}

debt_category_spec = {
    "OUTCOME_CODES": {"DA", "DC", "DD", "DG", "DH", "DI", "DU", "DV", "DW", "DX", "DY", "DZ"},
    "MATTER_TYPE1": {"DPDE", "DNPD", "DMDE", "DMCA", "DMAP", "DIVB", "DORH", "DTOT"},
    "MATTER_TYPE2": {"DVAL", "DMIX", "DCRE", "DIBP", "DORD", "DOTH", "DSCH"},
    "STAGE_REACHED": {"DA", "DB", "DC", "DD"},
}
discrimination_category_spec = {
    "OUTCOME_CODES": {
        "QA",
        "QB",
        "QC",
        "QD",
        "QE",
        "QF",
        "QG",
        "QH",
        "QI",
        "QJ",
        "QK",
        "QL",
        "QM",
        "QT",
        "QU",
        "QV",
        "QW",
        "QX",
        "QY",
        "QZ",
    },
    "MATTER_TYPE1": {"QPRO", "QEMP", "QEQP", "QPRE", "QFUN", "QEDU", "QPUB", "QCON"},
    "MATTER_TYPE2": {"QAGE", "QDIS", "QGEN", "QMCP", "QPRM", "QRAC", "QROB", "QSEX", "QSOR", "QMDI"},
    "STAGE_REACHED": {"QA", "QB", "QC", "QD", "QE", "QF", "QG", "QH"},
}
education_category_spec = {
    "OUTCOME_CODES": {
        "EA",
        "EB",
        "EC",
        "ED",
        "EE",
        "EF",
        "EG",
        "EH",
        "EI",
        "EJ",
        "EK",
        "EU",
        "EV",
        "EW",
        "EX",
        "EY",
        "EZ",
    },
    "MATTER_TYPE1": {"ESEN", "ENEG", "EXCE", "EDOT", "EADM", "EGTO", "EPRO", "EDDA", "EREO", "EEQU", "EDJR"},
    "MATTER_TYPE2": {"ENUR", "EDSC", "EPRU", "ECOL", "EUNI", "EAAP", "ELOC", "EIAP", "ESOS", "EHEF", "EOTH"},
    "STAGE_REACHED": {"EA", "EB", "EC", "ED"},
}
family_category_spec = {
    "OUTCOME_CODES": {
        "FA",
        "FB",
        "FC",
        "FD",
        "FE",
        "FF",
        "FG",
        "FH",
        "FI",
        "FJ",
        "FT",
        "FU",
        "FV",
        "FW",
        "FX",
        "FY",
        "FZ",
        "FS",
    },
    "MATTER_TYPE1": {
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
        "FAMT",
        "FAMU",
        "FAMV",
        "FAMW",
        "FAMX",
        "FAMY",
        "FAMZ",
        "FAM1",
        "FAM2",
        "FAM3",
    },
    "MATTER_TYPE2": {"FADV", "FPET", "FRES", "FAPP", "FREP", "FCHG", "FCHS", "FOTH", "FMEC", "FMEF", "FMEA"},
    "STAGE_REACHED": {"FA", "FB", "FC", "FD"},
}
housing_category_spec = {
    "OUTCOME_CODES": {
        "HA",
        "HD",
        "HE",
        "HF",
        "HG",
        "HH",
        "HI",
        "HJ",
        "HK",
        "HL",
        "HM",
        "HU",
        "HV",
        "HW",
        "HX",
        "HY",
        "HZ",
    },
    "MATTER_TYPE1": {"HRNT", "HMOR", "HPOT", "HANT", "HDIS", "HREP", "HREH", "HHOM", "HBFT", "HULE", "HLAN", "HOOT"},
    "MATTER_TYPE2": {"HPUB", "HPRI", "HHAC", "HNAS", "HOWN", "HHLS", "HLAN", "HOTH"},
    "STAGE_REACHED": {"HA", "HB", "HC", "HD"},
}
welfare_category_spec = {
    "OUTCOME_CODES": {"WA", "WB", "WC", "WD", "WE", "WG", "WU", "WV", "WZ"},
    "MATTER_TYPE1": {
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
        "WBUC",
    },
    "MATTER_TYPE2": {
        "WREA",
        "WREV",
        "WSSC",
        "WAPL",
        "WOVE",
        "WBAC",
        "WLGO",
        "WOTH",
        "WNAS",
        "WBPA",
        "WBUT",
        "WBCA",
        "WBSC",
        "WBHC",
    },
    "STAGE_REACHED": {"WA", "WB", "WC", "WD"},
}

contract_2013_category_spec = {
    "debt": deepcopy(debt_category_spec),
    "discrimination": deepcopy(discrimination_category_spec),
    "education": deepcopy(education_category_spec),
    "family": deepcopy(family_category_spec),
    "housing": deepcopy(housing_category_spec),
    "welfare": deepcopy(welfare_category_spec),
}

discrimination_category_spec["OUTCOME_CODES"].update({"QAA"})
family_category_spec["OUTCOME_CODES"].update({"FAA", "FAB", "FAC"})
housing_category_spec["OUTCOME_CODES"].update({"HAA", "HAB", "HAC"})
debt_category_spec["OUTCOME_CODES"].update({"DAA"})
education_category_spec["OUTCOME_CODES"].update({"EAA"})

contract_2018_category_spec = {
    "debt": deepcopy(debt_category_spec),
    "discrimination": deepcopy(discrimination_category_spec),
    "education": deepcopy(education_category_spec),
    "family": deepcopy(family_category_spec),
    "housing": deepcopy(housing_category_spec),
    "welfare": deepcopy(welfare_category_spec),
}


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
            elif case_matter_type_1 in contract_2018_category_spec["education"]["MATTER_TYPE1"]:
                return CONTRACT_EIGHTEEN_EDUCATION
            return CONTRACT_EIGHTEEN
    except TypeError:
        return CONTRACT_THIRTEEN
