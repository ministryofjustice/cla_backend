import itertools

SERVICE_ADAPTATIONS = {u'CBI', u'LLI', u'BSL', u'MIN', u'TYP', u'SWC', u'OAD',
                       u'TPC', u'TAF', u'FRS', u'NAR', u'OTH', u'MAR'}

EXEMPTION_CODES = {u'ECHI', u'EDET', u'EPRE'}

DISABILITY_INDICATOR = {u'NCD', u'MHC', u'LDD', u'ILL', u'OTH', u'UKN', u'MOB',
                        u'DEA',
                        u'HEA', u'VIS', u'BLI', u'PNS', u'PHY', u'SEN', u'COG'}

ADVICE_TYPES = {u'TA', u'OA', u'FF'}

AGE_RANGE = {u'A', u'B', u'C', u'D', u'E', u'F', u'G', u'U'}

ELIGIBILITY_CODES = {u'S', u'T', u'V', u'W', u'X', u'Z'}

DETERMINATION_CODES = {u'OOSC', u'OSPF', u'CHNM', u'FINI', u'DVCA'}

CATEGORY_SPEC = {
    u'debt': {
        'OUTCOME_CODES': {u'DA', u'DC', u'DD', u'DG', u'DH', u'DI', u'DU',
                          u'DV', u'DW', u'DX', u'DY', u'DZ'},
        'MATTER_TYPE1': {u'DPDE', u'DNPD', u'DMDE', u'DMCA', u'DMAP', u'DIVB',
                         u'DORH', u'DTOT', u'DSCH'},
        'MATTER_TYPE2': {u'DVAL', u'DMIX', u'DCRE', u'DIBP', u'DORD', u'DOTH'},
        'STAGE_REACHED': {u'DA', u'DB', u'DC', u'DD'}
    },
    u'discrimination': {
        'OUTCOME_CODES': {u'QA', u'QB', u'QC', u'QD', u'QE', u'QF', u'QG',
                          u'QH', u'QI', u'QJ', u'QK', u'QL', u'QM', u'QT',
                          u'QU', u'QV', u'QW', u'QX', u'QY', u'QZ'},
        'MATTER_TYPE1': {u'QPRO', u'QEMP', u'QEQP', u'QPRE', u'QFUN', u'QEDU',
                         u'QPUB', u'QCON'},
        'MATTER_TYPE2': {u'QAGE', u'QDIS', u'QGEN', u'QMCP', u'QPRM', u'QRAC',
                         u'QROB', u'QSEX', u'QSOR', u'QMDI'},
        'STAGE_REACHED': {u'QA', u'QB', u'QC', u'QD', u'QE', u'QF', u'QG',
                          u'QH'}
    },
    u'education': {
        'OUTCOME_CODES': {u'EA', u'EB', u'EC', u'ED', u'EE', u'EF', u'EG',
                          u'EH', u'EI', u'EJ', u'EK', u'EU', u'EV', u'EW',
                          u'EX', u'EY'},
        'MATTER_TYPE1': {u'ESEN', u'ENEG', u'EXCE', u'EDOT', u'EADM', u'EGTO',
                         u'EPRO', u'EDDA', u'EREO', u'EEQU'},
        'MATTER_TYPE2': {u'ENUR', u'EDSC', u'EPRU', u'ECOL', u'EUNI', u'EAAP',
                         u'ELOC', u'EIAP', u'ESOS', u'EHEF', u'EOTH'},
        'STAGE_REACHED': {u'EA', u'EB', u'EC', u'ED'}
    },
    u'family': {
        'OUTCOME_CODES': {u'FA', u'FB', u'FC', u'FD', u'FE', u'FF', u'FG',
                          u'FH', u'FI', u'FJ', u'FT', u'FU', u'FV', u'FW',
                          u'FX', u'FY', u'FZ', u'FS'},
        'MATTER_TYPE1': {u'FAMA', u'FAMB', u'FAMC', u'FAMD', u'FAME', u'FAMF',
                         u'FAMG', u'FAMH', u'FAMI', u'FAMJ', u'FAMK', u'FAML',
                         u'FAMM', u'FAMN', u'FAMO', u'FAMP', u'FAMQ', u'FAMR',
                         u'FAMS', u'FAMT', u'FAMU', u'FAMV', u'FAMW', u'FAMX',
                         u'FAMY', u'FAMZ', u'FAM1', u'FAM2', u'FAM3', },
        'MATTER_TYPE2': {u'FADV', u'FPET', u'FRES', u'FAPP', u'FREP', u'FCHG',
                         u'FCHS', u'FOTH', u'FMEC', u'FMEF', u'FMEA'},
        'STAGE_REACHED': {u'FA', u'FB', u'FC', u'FD'}
    },
    u'housing': {
        'OUTCOME_CODES': {u'HA', u'HD', u'HE', u'HF', u'HG', u'HH', u'HI',
                          u'HJ', u'HK', u'HL', u'HM', u'HU', u'HV', u'HW',
                          u'HX', u'HY', u'HZ'},
        'MATTER_TYPE1': {u'HRNT', u'HMOR', u'HPOT', u'HANT', u'HDIS', u'HREP',
                         u'HREH', u'HHOM', u'HBFT', u'HULE', u'HLAN', u'HOOT'},
        'MATTER_TYPE2': {u'HPUB', u'HPRI', u'HHAC', u'HNAS', u'HOWN', u'HHLS',
                         u'HLAN', u'HOTH'},
        'STAGE_REACHED': {u'HA', u'HB', u'HC', u'HD'}
    },
    u'welfare': {
        'OUTCOME_CODES': {u'WA', u'WB', u'WC', u'WD', u'WE', u'WG', u'WU',
                          u'WV', u'WZ'},
        'MATTER_TYPE1': {u'WDLA', u'WBAA', u'WICB', u'WSFP', u'WHBT', u'WIST',
                         u'WJSA', u'WIIB', u'WBBT', u'WTAX', u'WMUL', u'WOTH',
                         u'WESA', u'WBPI', u'WBUC'},
        'MATTER_TYPE2': {u'WREA', u'WREV', u'WSSC', u'WAPL', u'WOVE', u'WBAC',
                         u'WLGO', u'WOTH', u'WNAS', u'WBPA', u'WBUT', u'WBCA',
                         u'WBSC', u'WBHC'},
        'STAGE_REACHED': {u'WA', u'WB', u'WC', u'WD'}
    }
}

PREFIX_CATEGORY_LOOKUP = {
    u'D': u'debt',
    u'W': u'welfare',
    u'H': u'housing',
    u'F': u'family',
    u'E': u'education',
    u'Q': u'discrimination'
}

VALID_OUTCOMES = list(itertools.chain.from_iterable([v['OUTCOME_CODES'] for k, v in CATEGORY_SPEC.items()]))
VALID_STAGE_REACHED = list(itertools.chain.from_iterable([v['STAGE_REACHED'] for k, v in CATEGORY_SPEC.items()]))
VALID_MATTER_TYPE1 = list(itertools.chain.from_iterable([v['MATTER_TYPE1'] for k, v in CATEGORY_SPEC.items()]))
VALID_MATTER_TYPE2 = list(itertools.chain.from_iterable([v['MATTER_TYPE2'] for k, v in CATEGORY_SPEC.items()]))

STAGE_REACHED_REQUIRED_MT1S = {
    u'DMCA', u'DMAP', u'DIVB', u'DORH', u'DTOT', u'QPRO', u'QEMP', u'QEQP',
    u'QPRE', u'QFUN', u'QEDU', u'QPUB', u'QCON', u'ESEN', u'ENEG', u'EXCE',
    u'EDOT', u'EADM', u'EGTO', u'EPRO', u'EDDA', u'EREO', u'EEQU', u'HRNT',
    u'HPOT', u'HANT', u'HDIS', u'HREP', u'HHOM', u'HULE', u'HOOT', u'HPPO',
    u'HPWA', u'HRAR', u'HPOS', }

STAGE_REACHED_NOT_ALLOWED_MT1S = {
    u'WDLA', u'WBAA', u'WICB', u'WSFP', u'WHBT', u'WIST', u'WJSA', u'WIIB',
    u'WBBT', u'WTAX', u'WMUL', u'WOTH', u'WESA', u'WBPI', u'FAMA', u'FAMB',
    u'FAMC', u'FAMD', u'FAME', u'FAMF', u'FAMG', u'FAMH', u'FAMI', u'FAMJ',
    u'FAMK', u'FAML', u'FAMM', u'FAMN', u'FAMO', u'FAMP', u'FAMQ', u'FAMR',
    u'FAMS', u'FAMV', u'FAMW', u'FAMX', u'FAMY', u'FAMZ', u'FAM1', u'FAM2', u'FAM3'
}


POSTCODE_RE = r'''(?: # UK POSTCODE
    ( G[I1]R \s* [0O]AA | NFA | INT \s INT )           # special postcode
  |
    ( [A-PR-UWYZ01][A-Z01]? )       # area
    ( [0-9IO][0-9A-HJKMNPR-YIO]? )  # district
    (?: \s*
      ( [0-9IO] )                   # sector
      ( [ABD-HJLNPQ-Z10]{2} )       # unit
    )
)$'''
