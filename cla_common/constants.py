# -*- coding: utf-8 -*-
from os import environ as env
import datetime

from extended_choices import Choices


ELIGIBILITY_STATES = Choices(
    # constant, db_id, friendly string
    ("UNKNOWN", "unknown", "Unknown"),
    ("YES", "yes", "Yes"),
    ("NO", "no", "No"),
)

ELIGIBILITY_REASONS = Choices(
    # constant, db_id, friendly string
    ("DISPOSABLE_CAPITAL", "DISPOSABLE_CAPITAL", "Disposable capital too high"),
    ("GROSS_INCOME", "GROSS_INCOME", "Gross income too high"),
    ("DISPOSABLE_INCOME", "DISPOSABLE_INCOME", "Disposable income too high"),
)

TITLES = Choices(
    # constant, db_id, friendly string
    ("MR", "mr", "Mr"),
    ("MRS", "mrs", "Mrs"),
    ("MISS", "miss", "Miss"),
    ("MS", "ms", "Ms"),
    ("DR", "dr", "Dr"),
)


REQUIRES_ACTION_BY = Choices(
    # constant, db_id, friendly string
    # the Operator needs to take some actions (e.g. call the client)
    ("OPERATOR", "operator", "Operator"),
    # the Operator Manager needs to take some actions
    ("OPERATOR_MANAGER", "operator_manager", "Operator Manager"),
    # the Specialist needs to accept or reject the case
    ("PROVIDER_REVIEW", "1_provider_review", "Provider Review"),
    # the Specialist has accepted the case and the Case needs further work
    ("PROVIDER", "2_provider", "Provider"),
)

CALLBACK_TYPES = Choices(
    # constant, db_id, friendly string
    # Callback requested by a CHS Operator
    ("OPERATOR", "chs_operator", "CHS Operator"),
    # Callback requested for self via checker
    ("CHECKER_SELF", "web_form_self", "Web Form - Self"),
    # Callback requested for a third-party via checker
    ("CHECKER_THIRD_PARTY", "web_form_third_party", "Web Form - Third Party"),
)

CALLBACK_WINDOW_TYPES = Choices(
    # constant, db_id, friendly string
    (
        "HALF_HOUR_EITHER_SIDE",
        "HALF_HOUR_EITHER_SIDE",
        "Single time, with phone call up to 30 minutes before or after",
    ),
    ("HALF_HOUR_WINDOW", "HALF_HOUR_WINDOW", "Half hour time slot"),
)

MATTER_TYPE_LEVELS = Choices(
    # constant, db_id, friendly string
    ("ONE", 1, "1"),
    ("TWO", 2, "2"),
)

CASELOGTYPE_ACTION_KEYS = Choices(
    # constant, db_id, friendly string
    ("DECLINE_SPECIALISTS", "decline_specialists", "Decline Specialists"),
    ("DEFER_ASSIGNMENT", "defer_assign", "Defer Specialist Assignment"),
    ("PROVIDER_REJECT_CASE", "provider:reject_case", "Provider rejects the case"),
    ("PROVIDER_ACCEPT_CASE", "provider:accept_case", "Provider accepts the case"),
    ("PROVIDER_CLOSE_CASE", "provider:close_case", "Provider closes the case"),
)

THIRDPARTY_REASON = [
    ("CHILD_PATIENT", "Child or patient"),
    ("POWER_ATTORNEY", "Subject to power of attorney"),
    ("NO_TELEPHONE_DISABILITY", "Cannot communicate via the telephone, due to disability"),
    ("NO_TELEPHONE_LANGUAGE", "Cannot communicate via the telephone, due to a language requirement"),
    ("OTHER", "Other"),
]

THIRDPARTY_RELATIONSHIP = [
    ("PARENT_GUARDIAN", "Parent or guardian"),
    ("FAMILY_FRIEND", "Family member or friend"),
    ("PROFESSIONAL", "Professional"),
    ("LEGAL_ADVISOR", "Legal adviser"),
    ("OTHER", "Other"),
]

ADAPTATION_LANGUAGES = [
    ("ASSAMESE", "Assamese"),
    ("AZERI", "Azeri"),
    ("AFRIKAANS", "Afrikaans"),
    ("ALGERIAN", "Algerian"),
    ("ASHANTI", "Ashanti"),
    ("AKAN", "Akan"),
    ("ALBANIAN", "Albanian"),
    ("AMHARIC", "Amharic"),
    ("ARMENIAN", "Armenian"),
    ("ARABIC", "Arabic"),
    ("ASSYRIAN", "Assyrian"),
    ("AZERBAIJANI", "Azerbaijani"),
    ("BADINI", "Badini"),
    ("BENGALI", "Bengali"),
    ("BURMESE", "Burmese"),
    ("BAJUNI", "Bajuni"),
    ("BELORUSSIAN", "Belorussian"),
    ("BOSNIAN", "Bosnian"),
    ("BERBER", "Berber"),
    ("BASQUE", "Basque"),
    ("BULGARIAN", "Bulgarian"),
    ("BRAVA", "Brava"),
    ("BRAZILIAN", "Brazilian"),
    ("CANTONESE", "Cantonese"),
    ("CEBUANO", "Cebuano"),
    ("CREOLE", "Creole"),
    ("CHINESE", "Chinese"),
    ("CHEROKEE", "Cherokee"),
    ("COLUMBIAN", "Columbian"),
    ("CAMBODIAN", "Cambodian"),
    ("CHAOCHOW", "Chaochow"),
    ("CROATIAN", "Croatian"),
    ("CATALAN", "Catalan"),
    ("CZECH", "Czech"),
    ("DANISH", "Danish"),
    ("DARI", "Dari"),
    ("DUTCH", "Dutch"),
    ("EGYPTIAN", "Egyptian"),
    ("ENGLISH", "English"),
    ("ESTONIAN", "Estonian"),
    ("ERITREAN", "Eritrean"),
    ("ESPERANTO", "Esperanto"),
    ("ETHIOPIAN", "Ethiopian"),
    ("FARSI", "Farsi"),
    ("FIJIAN", "Fijian"),
    ("FLEMISH", "Flemish"),
    ("FANTI", "Fanti"),
    ("FRENCH", "French"),
    ("FINNISH", "Finnish"),
    ("FULLA", "Fulla"),
    ("GA", "Ga"),
    ("GERMAN", "German"),
    ("GURMUKHI", "Gurmukhi"),
    ("GAELIC", "Gaelic"),
    ("GORANI", "Gorani"),
    ("GEORGIAN", "Georgian"),
    ("GREEK", "Greek"),
    ("GUJARATI", "Gujarati"),
    ("HAKKA", "Hakka"),
    ("HEBREW", "Hebrew"),
    ("HINDI", "Hindi"),
    ("HOMA", "Homa"),
    ("HAUSA", "Hausa"),
    ("HUNGARIAN", "Hungarian"),
    ("HUI", "Hui"),
    ("ICELANDIC", "Icelandic"),
    ("IGBO", "Igbo"),
    ("ILOCANO", "Ilocano"),
    ("INDONESIAN", "Indonesian"),
    ("IRAQI", "Iraqi"),
    ("IRANIAN", "Iranian"),
    ("ITALIAN", "Italian"),
    ("JAPANESE", "Japanese"),
    ("KASHMIRI", "Kashmiri"),
    ("KREO", "Kreo"),
    ("KIRUNDI", "Kirundi"),
    ("KURMANJI", "Kurmanji"),
    ("KANNADA", "Kannada"),
    ("KOREAN", "Korean"),
    ("KRIO", "Krio"),
    ("KOSOVAN", "Kosovan"),
    ("KURDISH", "Kurdish"),
    ("KINYARWANDA", "Kinyarwanda"),
    ("KINYAMIRENGE", "Kinyamirenge"),
    ("KAZAKH", "Kazakh"),
    ("LATVIAN", "Latvian"),
    ("LAOTIAN", "Laotian"),
    ("LAO", "Lao"),
    ("LUBWISI", "Lubwisi"),
    ("LEBANESE", "Lebanese"),
    ("LINGALA", "Lingala"),
    ("LUO", "Luo"),
    ("LUSOGA", "Lusoga"),
    ("LITHUANIAN", "Lithuanian"),
    ("LUGANDA", "Luganda"),
    ("MANDARIN", "Mandarin"),
    ("MACEDONIAN", "Macedonian"),
    ("MOLDOVAN", "Moldovan"),
    ("MIRPURI", "Mirpuri"),
    ("MANDINKA", "Mandinka"),
    ("MALAY", "Malay"),
    ("MONGOLIAN", "Mongolian"),
    ("MOROCCAN", "Moroccan"),
    ("MARATHI", "Marathi"),
    ("MALTESE", "Maltese"),
    ("MALAYALAM", "Malayalam"),
    ("NDEBELE", "Ndebele"),
    ("NEPALESE", "Nepalese"),
    ("NIGERIAN", "Nigerian"),
    ("NORWEGIAN", "Norwegian"),
    ("NYAKUSE", "Nyakuse"),
    ("OROMO", "Oromo"),
    ("OTHER", "Other"),
    ("PAHARI", "Pahari"),
    ("PERSIAN", "Persian"),
    ("PORTUGUESE", "Portuguese"),
    ("PHILIPINO", "Philipino"),
    ("POLISH", "Polish"),
    ("POTHWARI", "Pothwari"),
    ("PUSTHU", "Pusthu"),
    ("PUNJABI", "Punjabi"),
    ("ROMANIAN", "Romanian"),
    ("RUSSIAN", "Russian"),
    ("SOTHO", "Sotho"),
    ("SERBO-CROAT", "Serbo-Croat"),
    ("SWEDISH", "Swedish"),
    ("SERBIAN", "Serbian"),
    ("SHONA", "Shona"),
    ("SINHALESE", "Sinhalese"),
    ("SIRAIKI", "Siraiki"),
    ("SLOVAK", "Slovak"),
    ("SAMOAN", "Samoan"),
    ("SLOVENIAN", "Slovenian"),
    ("SOMALI", "Somali"),
    ("SORANI", "Sorani"),
    ("SPANISH", "Spanish"),
    ("SRI LANKAN", "Sri Lankan"),
    ("SCOTTISH GAELIC", "Scottish Gaelic"),
    ("SUDANESE", "Sudanese"),
    ("SWAHILI", "Swahili"),
    ("SWAHILLI", "Swahilli"),
    ("SYLHETI", "Sylheti"),
    ("TAMIL", "Tamil"),
    ("TIBETAN", "Tibetan"),
    ("TELEGU", "Telegu"),
    ("ELAKIL", "Elakil"),
    ("TAGALOG", "Tagalog"),
    ("THAI", "Thai"),
    ("TIGRINIAN", "Tigrinian"),
    ("TIGRE", "Tigre"),
    ("TAJIK", "Tajik"),
    ("TAIWANESE", "Taiwanese"),
    ("TURKMANISH", "Turkmanish"),
    ("TSWANA", "Tswana"),
    ("TURKISH", "Turkish"),
    ("TWI", "Twi"),
    ("UGANDAN", "Ugandan"),
    ("UKRANIAN", "Ukranian"),
    ("URDU", "Urdu"),
    ("USSIAN", "Ussian"),
    ("UZBEK", "Uzbek"),
    ("VIETNAMESE", "Vietnamese"),
    ("WELSH", "Welsh"),
    ("WOLOF", "Wolof"),
    ("XHOSA", "Xhosa"),
    ("YUGOSLAVIAN", "Yugoslavian"),
    ("YIDDISH", "Yiddish"),
    ("YORUBA", "Yoruba"),
    ("ZULU", "Zulu"),
]

DIAGNOSIS_SCOPE = Choices(
    # constant, db_id, friendly string
    ("INSCOPE", "INSCOPE", "In Scope"),
    ("OUTOFSCOPE", "OUTOFSCOPE", "Out of Scope"),
    ("UNKNOWN", "UNKNOWN", "Unknown (Diagnosis not complete)"),
    ("CONTACT", "CONTACT", "In Scope - skip means test"),
    ("INELIGIBLE", "INELIGIBLE", "Problem not covered"),
    ("MEDIATION", "MEDIATION", "Advice for mediation"),
)

CONTACT_SAFETY = Choices(
    # constant, db_id, friendly string
    ("SAFE", "SAFE", "Safe to contact"),
    ("DONT_CALL", "DONT_CALL", "Not safe to call"),
)

EMAIL_SAFETY = Choices(
    # constant, db_id, friendly string
    ("SAFE", "SAFE", "Safe to email"),
    ("DONT_EMAIL", "DONT_EMAIL", "Not safe to email"),
)

EXEMPT_USER_REASON = Choices(
    # constant, db_id, friendly string
    ("ECHI", "ECHI", "Client is a child"),
    ("EDET", "EDET", "Client is in detention"),
    ("EPRE", "EPRE", "12 month exemption"),
)

ECF_OPTIONS = [
    {
        "key": "XFER_TO_RECORDED_MESSAGE",
        "label": "Transferring inbound call to recorded message? Read out the following statement:",
        "text": """
        "On closing this call you will hear a recorded message which will contain information to highlight limited
         circumstances in which legal aid may still be available to you. Thank you [client name] for calling
         Civil Legal Advice. Goodbye"
        """,
    },
    {
        "key": "READ_OUT_MESSAGE",
        "label": "Outbound call? Read out the following statement:",
        "text": """
        "Legal aid may be available in exceptional circumstances to people whose cases are out of scope where a refusal
         to fund would breach Human Rights or enforceable European law. You could seek advice from a legal advisor
         about whether an application might succeed in your case and how to make one. Thank you for calling
         Civil Legal Advice. Goodbye"
        """,
    },
    {"key": "PROBLEM_NOT_SUITABLE", "label": "Problem not suitable for ECF message", "text": ""},
    {"key": "CLIENT_TERMINATED", "label": "Could not provide - client terminated call", "text": ""},
]

ECF_STATEMENT = Choices(
    # constant, db_id, friendly string
    *[(x["key"], x["key"], x["text"]) for x in ECF_OPTIONS]
)


FEEDBACK_ISSUE = Choices(
    # constant, db_id, friendly string
    ("ADVISOR_CONDUCT", "ADCO", "Advisor conduct"),
    ("ACCESS_PROBLEMS", "ACPR", "Access problems"),
    ("ALREADY_RECEIVING_ADVICE", "ARRA", "Already receiving/received advice"),
    ("WRONG_CATEGORY", "COLI", "Category of law is incorrect"),
    ("DELAY_ADVISING_LACK_OF_FOLLOWUP_INFORMATION", "DLAY", "Delay in advising (lack of follow up information)"),
    ("DELAY_ADVISING_OTHER", "DLAO", "Delay in advising (other)"),
    ("INCORRECT_ELIGIBILITY_CALCULATION", "INEL", "Incorrect eligibility calculation"),
    ("INCORRECT_DIAGNOSIS", "INDI", "Incorrect diagnosis (out of scope)"),
    ("INCORRECT_INFO_DIAGNOSIS", "INIP", "Incorrect information provided (diagnosis)"),
    ("INCORRECT_XFER_PROVIDER", "INTC", "Incorrect transferring of calls (provider)"),
    ("INCORRECT_XFER_BACKDOOR", "INFB", "Incorrect transferring of calls (front/back)"),
    ("INCORRECT_OR_MISSING_PERSONAL_DETAILS", "IMCD", "Incorrect/missing contact details or DOB"),
    ("OTHER_DATA_ENTRY_ERROR", "ODDE", "Other data entry errors"),
    ("SYSTEM_ERROR", "SESE", "System Error"),
    ("OTHER", "OTHR", "Other"),
)


SOCKETIO_CLIENT_CONFIG = {"SOCKETIO_SERVER_URL": env.get("SOCKETIO_SERVER_URL", "http://localhost:8005")}


RESEARCH_CONTACT_VIA = Choices(
    # constant, db_id, friendly string
    ("EMAIL", "EMAIL", "Email"),
    ("PHONE", "PHONE", "Phone"),
    ("SMS", "SMS", "Sms"),
)


CASE_SOURCE = Choices(
    # constant, db_id, friendly string
    ("PHONE", "PHONE", "Phone"),
    ("VOICEMAIL", "VOICEMAIL", "Voicemail"),
    ("SMS", "SMS", "Sms"),
    ("WEB", "WEB", "Web"),
)


GENDERS = Choices(
    # constant, db_id, friendly string
    ("PNS", "Prefer not to say", "Prefer not to say"),
    ("MALE", "Male", "Male"),
    ("FEMALE", "Female", "Female"),
)


ETHNICITIES = Choices(
    # constant, db_id, friendly string
    ("PNS", "Prefer not to say", "Prefer not to say"),
    ("NOT_ASKED", "Client Not Asked", "Client Not Asked"),
    ("WHITE_BRITISH", "White British", "White: British"),
    ("WHITE_IRISH", "White Irish", "White: Irish"),
    ("BLACK_CARIBBEAN", "Black or Black British Caribbean", "Black or Black British: Caribbean"),
    ("BLACK_AFRICAN", "Black or Black British African", "Black or Black British: African"),
    ("BLACK_OTHER", "Black or Black British Other", "Black or Black British: Other"),
    ("ASIAN_INDIAN", "Asian or Asian British Indian", "Asian or Asian British: Indian"),
    ("ASIAN_PAKISTANI", "Asian or Asian British Pakistani", "Asian or Asian British: Pakistani"),
    ("ASIAN_BANGLADESHI", "Asian or Asian British Bangladeshi", "Asian or Asian British: Bangladeshi"),
    ("ASIAN_OTHER", "Asian or Asian British Other", "Asian or Asian British: Other"),
    ("CHINESE", "Chinese", "Chinese"),
    ("MIXED_BLACK_CARIBBEAN", "Mixed White and Black Caribbean", "Mixed: White and Black Caribbean"),
    ("MIXED_BLACK_AFRICAN", "Mixed White and Black African", "Mixed: White and Black African"),
    ("MIXED_ASIAN", "Mixed White and Asian", "Mixed: White and Asian"),
    ("MIXED_OTHER", "Mixed Other", "Mixed: Other"),
    ("GYPSY", "Gypsy/Traveller", "Gypsy/Traveller"),
    ("OTHER", "Other", "Other"),
)

ETHNICITIES_GROUPS = {
    "WHITE": (ETHNICITIES.WHITE_BRITISH, ETHNICITIES.WHITE_IRISH),
    "BLACK": (ETHNICITIES.BLACK_CARIBBEAN, ETHNICITIES.BLACK_AFRICAN, ETHNICITIES.BLACK_OTHER),
    "ASIAN": (
        ETHNICITIES.ASIAN_INDIAN,
        ETHNICITIES.ASIAN_PAKISTANI,
        ETHNICITIES.ASIAN_BANGLADESHI,
        ETHNICITIES.ASIAN_OTHER,
    ),
    "MIXED": (
        ETHNICITIES.MIXED_BLACK_CARIBBEAN,
        ETHNICITIES.MIXED_BLACK_AFRICAN,
        ETHNICITIES.MIXED_ASIAN,
        ETHNICITIES.MIXED_OTHER,
    ),
}


RELIGIONS = Choices(
    # constant, db_id, friendly string
    ("PNS", "Prefer not to say", "Prefer not to say"),
    ("CHRISTIAN", "Christian", "Christian"),
    ("MUSLIM", "Muslim", "Muslim"),
    ("HINDU", "Hindu", "Hindu"),
    ("SIKH", "Sikh", "Sikh"),
    ("JEWISH", "Jewish", "Jewish"),
    ("BUDDHIST", "Buddhist", "Buddhist"),
    ("NO_RELIGION", "No religion", "No religion"),
    ("OTHER", "other ", "other "),
)


SEXUAL_ORIENTATIONS = Choices(
    # constant, db_id, friendly string
    ("PNS", "Prefer Not To Say", "Prefer Not To Say"),
    ("HETEROSEXUAL", "Heterosexual", "Heterosexual"),
    ("GAY_MAN", "Gay man", "Gay man"),
    ("GAY_WOMAN", "Gay woman", "Gay woman"),
    ("BISEXUAL", "Bisexual", "Bisexual"),
    ("OTHER", "Other", "Other"),
)


DISABILITIES = Choices(
    # constant, db_id, friendly string
    ("PNS", "PNS - Prefer not to say", "Prefer not to say"),
    ("NCD", "NCD - Not Considered Disabled", "Not Considered Disabled"),
    ("MOB", "MOB - Mobility impairment", "Mobility impairment"),
    ("HEA", "HEA - Hearing impaired", "Hearing impaired"),
    ("DEA", "DEA - Deaf", "Deaf"),
    ("VIS", "VIS - Visually impaired", "Visually impaired"),
    ("BLI", "BLI - Blind", "Blind"),
    ("LDD", "LDD - Learning Disability/Difficulty", "Learning Disability/Difficulty"),
    ("MHC", "MHC - Mental Health Condition", "Mental Health Condition"),
    ("ILL", "ILL - Long-Standing Illness Or Health Condition", "Long-Standing Illness Or Health Condition"),
    ("UKN", "UKN - Unknown", "Unknown"),
    ("OTH", "OTH - Other", "Other"),
)


SPECIFIC_BENEFITS = Choices(
    # constant, db_id, friendly string
    ("UNIVERSAL_CREDIT", "universal_credit", "Universal credit"),
    ("INCOME_SUPPORT", "income_support", "Income Support"),
    ("JOB_SEEKERS_ALLOWANCE", "job_seekers_allowance", "Income-based Job Seekers Allowance"),
    ("PENSION_CREDIT", "pension_credit", "Guarantee State Pension Credit"),
    ("EMPLOYMENT_SUPPORT", "employment_support", "Income-related Employment and Support Allowance"),
)


DISREGARDS = Choices(
    # constant, db_id, friendly string
    ("BENEFIT_PAYMENTS", "benefit_payments", "Backdated benefit payments"),
    ("CHILD_MAINTENANCE", "child_maintenance", "Backdated child maintenance payments"),
    ("ENERGY_PRICES", "energy_prices", "The Energy Support Scheme payments (2022 and 2023)"),
    ("COST_LIVING", "cost_living", "Cost of living payments"),
    ("INFECTED_BLOOD", "infected_blood", "Infected Blood Support Scheme"),
    ("CRIMINAL_INJURIES", "criminal_injuries", "Criminal Injuries Compensation Scheme"),
    ("GRENFELL_TOWER", "grenfell_tower", "Grenfell Tower compensation"),
    ("MODERN_SLAVERY", "modern_slavery", "Modern Slavery Victim Care Contract or National Referral Mechanism (NRM)"),
    ("NATIONAL_EMERGENCIES", "national_emergencies", "National Emergencies Trust"),
    ("LONDON_EMERGENCIES", "london_emergencies", "London Emergencies Trust"),
    ("VCJD_TRUST", "vcjd_trust", "vCJD Trust"),
    ("VACCINE_DAMAGE", "vaccine_damage", "Vaccine Damage Payment"),
    ("OVERSEAS_TERRORISM", "overseas_terrorism", "Victims of Overseas Terrorism Compensation Scheme (VOTCS)"),
    ("CHILD_ABUSE", "child_abuse", "Scotland and Northern Ireland redress schemes for historical child abuse"),
    ("JUSTICE_COMPENSATION", "justice_compensation", "Miscarriage of justice compensation"),
    ("LOVE_MANCHESTER", "love_manchester", "We Love Manchester Emergency Fund"),
)


EXPRESSIONS_OF_DISSATISFACTION = Choices(
    # constant, db_id, friendly string
    ("INCORRECT", "incorrect", "Believes operator has given incorrect information"),
    ("SCOPE", "scope", "Unhappy with Operator Service determination (Scope)"),
    ("MEANS", "means", "Unhappy with Operator Service determination (Means)"),
    ("DELETE", "delete", "Wants personal details deleted"),
    ("ADVISOR_RESPONSE", "advisor_response", "No response from specialist advisor, or response delayed"),
    ("OPERATOR_DELAY", "operator_delay", "Operator service - delay in advice"),
    ("OPERATOR_ATTITUDE", "operator_attitude", "Unhappy with operator's attitude"),
    ("ADVISOR_ATTITUDE", "advisor_attitude", "Unhappy with specialist's attitude"),
    ("ALT_HELP", "alt_help", "Alternative help not appropriate or not available"),
    ("PUBLIC_TOOL", "public_tool", "Unhappy with online service"),
    ("ADAPTATIONS", "adaptations", "Problems with adaptations or adjustments"),
    ("SCOPE_ASSESSMENT", "scope_assessment", "Scope reassessment requested"),
    ("MEANS_ASSESSMENT", "means_assessment", "Financial reassessment requested"),
    (
        "PASS_TO_PUBLIC",
        "pass_to_public",
        "Threatens to pass the matter on to the media, " "or other public or regulatory body",
    ),
    ("DATA_PROTECTION", "data_protection", "Breach of Data Protection Act/policy and confidentiality"),
    ("DISCRIMINATION", "discrimination", "Discrimination from an operator or specialist"),
    ("PLO_REFERRAL", "plo_referral", "Client unhappy with PLO referral"),
    ("OTHER", "other", "Other"),
)
EXPRESSIONS_OF_DISSATISFACTION_FLAGS = {
    # constant: [allowed flags; currently only 'minor' and 'major' are permitted]
    EXPRESSIONS_OF_DISSATISFACTION.INCORRECT: ("minor", "major"),
    EXPRESSIONS_OF_DISSATISFACTION.SCOPE: ("minor",),
    EXPRESSIONS_OF_DISSATISFACTION.MEANS: ("minor",),
    EXPRESSIONS_OF_DISSATISFACTION.DELETE: ("minor",),
    EXPRESSIONS_OF_DISSATISFACTION.ADVISOR_RESPONSE: ("minor", "major"),
    EXPRESSIONS_OF_DISSATISFACTION.OPERATOR_DELAY: ("minor", "major"),
    EXPRESSIONS_OF_DISSATISFACTION.OPERATOR_ATTITUDE: ("major",),
    EXPRESSIONS_OF_DISSATISFACTION.ADVISOR_ATTITUDE: ("major",),
    EXPRESSIONS_OF_DISSATISFACTION.ALT_HELP: ("minor",),
    EXPRESSIONS_OF_DISSATISFACTION.PUBLIC_TOOL: ("minor",),
    EXPRESSIONS_OF_DISSATISFACTION.ADAPTATIONS: ("minor",),
    EXPRESSIONS_OF_DISSATISFACTION.SCOPE_ASSESSMENT: ("major",),
    EXPRESSIONS_OF_DISSATISFACTION.MEANS_ASSESSMENT: ("major",),
    EXPRESSIONS_OF_DISSATISFACTION.PASS_TO_PUBLIC: ("major",),
    EXPRESSIONS_OF_DISSATISFACTION.DATA_PROTECTION: ("major",),
    EXPRESSIONS_OF_DISSATISFACTION.DISCRIMINATION: ("major",),
    EXPRESSIONS_OF_DISSATISFACTION.PLO_REFERRAL: ("major",),
    EXPRESSIONS_OF_DISSATISFACTION.OTHER: ("minor",),
    # TODO: shouldn't EXPRESSIONS_OF_DISSATISFACTION.OTHER allow 'major' too as a catch-all?
}

REASONS_FOR_CONTACTING = Choices(
    # NB: these are duplicated (for translation) in cla_public so change both when necessary!
    # constant, db_id, *english* friendly string
    ("CANT_ANSWER", "CANT_ANSWER", u"I don’t know how to answer a question"),
    ("MISSING_PAPERWORK", "MISSING_PAPERWORK", u"I don’t have the paperwork I need"),
    ("PREFER_SPEAKING", "PREFER_SPEAKING", u"I’d prefer to speak to someone"),
    ("DIFFICULTY_ONLINE", "DIFFICULTY_ONLINE", u"I have trouble using online services"),
    ("HOW_SERVICE_HELPS", "HOW_SERVICE_HELPS", u"I don’t understand how this service can help me"),
    ("AREA_NOT_COVERED", "AREA_NOT_COVERED", u"My problem area isn’t covered"),
    ("PNS", "PNS", u"I’d prefer not to say"),
    ("OTHER", "OTHER", u"Another reason"),
)

OPERATOR_HOURS = {
    "weekday": (datetime.time(9, 0), datetime.time(20, 0)),
    "saturday": (datetime.time(9, 0), datetime.time(12, 30)),
    "2021-12-24": (datetime.time(9, 0), datetime.time(17, 00)),
    "2020-12-24": (datetime.time(9, 0), datetime.time(17, 00)),
    "2020-12-31": (datetime.time(9, 0), datetime.time(17, 00)),
    "2020-12-26": (None, None),
    "2021-12-31": (datetime.time(9, 0), datetime.time(17, 00)),
    "2023-07-27": (None, None),
    "2023-07-28": (None, None),
}

# Represents a users financial eligibility status from check if you can get legal aid
FINANCIAL_ASSESSMENT_STATUSES = Choices(
    # constant, db_id, display string
    ("PASSED", "PASSED", "Passed"),
    ("FAILED", "FAILED", "Failed"),
    ("FAST_TRACK", "FAST_TRACK", "Client told to call the helpline for the assessment."),
    # Operationally fast tracked through the check if you can get legal aid means test
    # E.g. due to risk of harm, are under 18, have trapped capital etc.
    ("SKIPPED", "SKIPPED", "No details. Client called the helpline directly.")
    # The client skipped the financial assessment due to clicking "Contact Us" directly.
)

# Why the user was fast tracked through the check if you can get legal aid means test
FAST_TRACK_REASON = Choices(
    # constant, db_id, display string
    ("HARM", "HARM", "User has indicated they are at risk of harm"),
    ("MORE_INFO_REQUIRED", "MORE_INFO_REQUIRED", "Further scoping information is required"),
    ("OTHER", "OTHER", "Other"),
)
