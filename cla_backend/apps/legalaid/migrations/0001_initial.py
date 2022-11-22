# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import models, migrations
import django.db.models.deletion
import django.utils.timezone

import core.cloning
import cla_common.db.mixins
import cla_common.money_interval.fields
import model_utils.fields
import jsonfield.fields
import uuidfield.fields
import legalaid.fields


class Migration(migrations.Migration):

    dependencies = [
        ("knowledgebase", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("diagnosis", "0001_initial"),
        ("cla_provider", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdaptationDetails",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("bsl_webcam", models.BooleanField(default=False)),
                ("minicom", models.BooleanField(default=False)),
                ("text_relay", models.BooleanField(default=False)),
                ("skype_webcam", models.BooleanField(default=False)),
                (
                    "language",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        null=True,
                        choices=[
                            (b"ASSAMESE", b"Assamese"),
                            (b"AZERI", b"Azeri"),
                            (b"AFRIKAANS", b"Afrikaans"),
                            (b"ALGERIAN", b"Algerian"),
                            (b"ASHANTI", b"Ashanti"),
                            (b"AKAN", b"Akan"),
                            (b"ALBANIAN", b"Albanian"),
                            (b"AMHARIC", b"Amharic"),
                            (b"ARMENIAN", b"Armenian"),
                            (b"ARABIC", b"Arabic"),
                            (b"ASSYRIAN", b"Assyrian"),
                            (b"AZERBAIJANI", b"Azerbaijani"),
                            (b"BADINI", b"Badini"),
                            (b"BENGALI", b"Bengali"),
                            (b"BURMESE", b"Burmese"),
                            (b"BAJUNI", b"Bajuni"),
                            (b"BELORUSSIAN", b"Belorussian"),
                            (b"BOSNIAN", b"Bosnian"),
                            (b"BERBER", b"Berber"),
                            (b"BASQUE", b"Basque"),
                            (b"BULGARIAN", b"Bulgarian"),
                            (b"BRAVA", b"Brava"),
                            (b"BRAZILIAN", b"Brazilian"),
                            (b"CANTONESE", b"Cantonese"),
                            (b"CEBUANO", b"Cebuano"),
                            (b"CREOLE", b"Creole"),
                            (b"CHINESE", b"Chinese"),
                            (b"CHEROKEE", b"Cherokee"),
                            (b"COLUMBIAN", b"Columbian"),
                            (b"CAMBODIAN", b"Cambodian"),
                            (b"CHAOCHOW", b"Chaochow"),
                            (b"CROATIAN", b"Croatian"),
                            (b"CATALAN", b"Catalan"),
                            (b"CZECH", b"Czech"),
                            (b"DANISH", b"Danish"),
                            (b"DARI", b"Dari"),
                            (b"DUTCH", b"Dutch"),
                            (b"EGYPTIAN", b"Egyptian"),
                            (b"ENGLISH", b"English"),
                            (b"ESTONIAN", b"Estonian"),
                            (b"ERITREAN", b"Eritrean"),
                            (b"ESPERANTO", b"Esperanto"),
                            (b"ETHIOPIAN", b"Ethiopian"),
                            (b"FARSI", b"Farsi"),
                            (b"FIJIAN", b"Fijian"),
                            (b"FLEMISH", b"Flemish"),
                            (b"FANTI", b"Fanti"),
                            (b"FRENCH", b"French"),
                            (b"FINNISH", b"Finnish"),
                            (b"FULLA", b"Fulla"),
                            (b"GA", b"Ga"),
                            (b"GERMAN", b"German"),
                            (b"GURMUKHI", b"Gurmukhi"),
                            (b"GAELIC", b"Gaelic"),
                            (b"GORANI", b"Gorani"),
                            (b"GEORGIAN", b"Georgian"),
                            (b"GREEK", b"Greek"),
                            (b"GUJARATI", b"Gujarati"),
                            (b"HAKKA", b"Hakka"),
                            (b"HEBREW", b"Hebrew"),
                            (b"HINDI", b"Hindi"),
                            (b"HOMA", b"Homa"),
                            (b"HAUSA", b"Hausa"),
                            (b"HUNGARIAN", b"Hungarian"),
                            (b"HUI", b"Hui"),
                            (b"ICELANDIC", b"Icelandic"),
                            (b"IGBO", b"Igbo"),
                            (b"ILOCANO", b"Ilocano"),
                            (b"INDONESIAN", b"Indonesian"),
                            (b"IRAQI", b"Iraqi"),
                            (b"IRANIAN", b"Iranian"),
                            (b"ITALIAN", b"Italian"),
                            (b"JAPANESE", b"Japanese"),
                            (b"KASHMIRI", b"Kashmiri"),
                            (b"KREO", b"Kreo"),
                            (b"KIRUNDI", b"Kirundi"),
                            (b"KURMANJI", b"Kurmanji"),
                            (b"KANNADA", b"Kannada"),
                            (b"KOREAN", b"Korean"),
                            (b"KRIO", b"Krio"),
                            (b"KOSOVAN", b"Kosovan"),
                            (b"KURDISH", b"Kurdish"),
                            (b"KINYARWANDA", b"Kinyarwanda"),
                            (b"KINYAMIRENGE", b"Kinyamirenge"),
                            (b"KAZAKH", b"Kazakh"),
                            (b"LATVIAN", b"Latvian"),
                            (b"LAOTIAN", b"Laotian"),
                            (b"LAO", b"Lao"),
                            (b"LUBWISI", b"Lubwisi"),
                            (b"LEBANESE", b"Lebanese"),
                            (b"LINGALA", b"Lingala"),
                            (b"LUO", b"Luo"),
                            (b"LUSOGA", b"Lusoga"),
                            (b"LITHUANIAN", b"Lithuanian"),
                            (b"LUGANDA", b"Luganda"),
                            (b"MANDARIN", b"Mandarin"),
                            (b"MACEDONIAN", b"Macedonian"),
                            (b"MOLDOVAN", b"Moldovan"),
                            (b"MIRPURI", b"Mirpuri"),
                            (b"MANDINKA", b"Mandinka"),
                            (b"MALAY", b"Malay"),
                            (b"MONGOLIAN", b"Mongolian"),
                            (b"MOROCCAN", b"Moroccan"),
                            (b"MARATHI", b"Marathi"),
                            (b"MALTESE", b"Maltese"),
                            (b"MALAYALAM", b"Malayalam"),
                            (b"NDEBELE", b"Ndebele"),
                            (b"NEPALESE", b"Nepalese"),
                            (b"NIGERIAN", b"Nigerian"),
                            (b"NORWEGIAN", b"Norwegian"),
                            (b"NYAKUSE", b"Nyakuse"),
                            (b"OROMO", b"Oromo"),
                            (b"OTHER", b"Other"),
                            (b"PAHARI", b"Pahari"),
                            (b"PERSIAN", b"Persian"),
                            (b"PORTUGUESE", b"Portuguese"),
                            (b"PHILIPINO", b"Philipino"),
                            (b"POLISH", b"Polish"),
                            (b"POTHWARI", b"Pothwari"),
                            (b"PUSTHU", b"Pusthu"),
                            (b"PUNJABI", b"Punjabi"),
                            (b"ROMANIAN", b"Romanian"),
                            (b"RUSSIAN", b"Russian"),
                            (b"SOTHO", b"Sotho"),
                            (b"SERBO-CROAT", b"Serbo-Croat"),
                            (b"SWEDISH", b"Swedish"),
                            (b"SERBIAN", b"Serbian"),
                            (b"SHONA", b"Shona"),
                            (b"SINHALESE", b"Sinhalese"),
                            (b"SIRAIKI", b"Siraiki"),
                            (b"SLOVAK", b"Slovak"),
                            (b"SAMOAN", b"Samoan"),
                            (b"SLOVENIAN", b"Slovenian"),
                            (b"SOMALI", b"Somali"),
                            (b"SORANI", b"Sorani"),
                            (b"SPANISH", b"Spanish"),
                            (b"SRI LANKAN", b"Sri Lankan"),
                            (b"SCOTTISH GAELIC", b"Scottish Gaelic"),
                            (b"SUDANESE", b"Sudanese"),
                            (b"SWAHILI", b"Swahili"),
                            (b"SWAHILLI", b"Swahilli"),
                            (b"SYLHETI", b"Sylheti"),
                            (b"TAMIL", b"Tamil"),
                            (b"TIBETAN", b"Tibetan"),
                            (b"TELEGU", b"Telegu"),
                            (b"ELAKIL", b"Elakil"),
                            (b"TAGALOG", b"Tagalog"),
                            (b"THAI", b"Thai"),
                            (b"TIGRINIAN", b"Tigrinian"),
                            (b"TIGRE", b"Tigre"),
                            (b"TAJIK", b"Tajik"),
                            (b"TAIWANESE", b"Taiwanese"),
                            (b"TURKMANISH", b"Turkmanish"),
                            (b"TSWANA", b"Tswana"),
                            (b"TURKISH", b"Turkish"),
                            (b"TWI", b"Twi"),
                            (b"UGANDAN", b"Ugandan"),
                            (b"UKRANIAN", b"Ukranian"),
                            (b"URDU", b"Urdu"),
                            (b"USSIAN", b"Ussian"),
                            (b"UZBEK", b"Uzbek"),
                            (b"VIETNAMESE", b"Vietnamese"),
                            (b"WELSH", b"Welsh"),
                            (b"WOLOF", b"Wolof"),
                            (b"XHOSA", b"Xhosa"),
                            (b"YUGOSLAVIAN", b"Yugoslavian"),
                            (b"YIDDISH", b"Yiddish"),
                            (b"YORUBA", b"Yoruba"),
                            (b"ZULU", b"Zulu"),
                        ],
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("callback_preference", models.BooleanField(default=False)),
                ("reference", uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
            ],
            options={"abstract": False},
            bases=(core.cloning.CloneModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Case",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("reference", models.CharField(unique=True, max_length=128, editable=False)),
                (
                    "requires_action_by",
                    models.CharField(
                        default=b"operator",
                        editable=False,
                        choices=[
                            (b"operator", b"Operator"),
                            (b"operator_manager", b"Operator Manager"),
                            (b"1_provider_review", b"Provider Review"),
                            (b"2_provider", b"Provider"),
                        ],
                        max_length=50,
                        blank=True,
                        null=True,
                    ),
                ),
                ("requires_action_at", models.DateTimeField(null=True, blank=True)),
                ("callback_attempt", models.PositiveSmallIntegerField(default=0)),
                ("locked_at", models.DateTimeField(null=True, blank=True)),
                ("notes", models.TextField(blank=True)),
                ("provider_notes", models.TextField(blank=True)),
                ("laa_reference", models.BigIntegerField(unique=True, null=True, editable=False, blank=True)),
                ("billable_time", models.PositiveIntegerField(default=0)),
                ("outcome_code", models.CharField(max_length=50, null=True, blank=True)),
                ("outcome_code_id", models.IntegerField(null=True, blank=True)),
                ("level", models.PositiveSmallIntegerField(null=True)),
                ("exempt_user", models.NullBooleanField()),
                (
                    "exempt_user_reason",
                    models.CharField(
                        blank=True,
                        max_length=5,
                        null=True,
                        choices=[
                            (b"ECHI", b"Client is a child"),
                            (b"EDET", b"Client is in detention"),
                            (b"EPRE", b"12 month exemption"),
                        ],
                    ),
                ),
                (
                    "ecf_statement",
                    models.CharField(
                        blank=True,
                        max_length=35,
                        null=True,
                        choices=[
                            (
                                b"XFER_TO_RECORDED_MESSAGE",
                                b'"On closing this call you will hear a recorded message which will contain information to highlight limited circumstances in which legal aid may still be available to you. Thank you [client name] for calling Civil Legal Advice. Goodbye"',
                            ),
                            (
                                b"READ_OUT_MESSAGE",
                                b'"Legal aid may be available in exceptional circumstances to people whose cases are out of scope where a refusal to fund would breach Human Rights or enforceable European law. You could seek advice from a legal advisor about whether an application might succeed in your case and how to make one. Thank you for calling Civil Legal Advice. Goodbye"',
                            ),
                            (b"PROBLEM_NOT_SUITABLE", b""),
                            (b"CLIENT_TERMINATED", b""),
                        ],
                    ),
                ),
                ("provider_assigned_at", models.DateTimeField(null=True, blank=True)),
                ("provider_viewed", models.DateTimeField(null=True, blank=True)),
                ("provider_accepted", models.DateTimeField(null=True, blank=True)),
                ("provider_closed", models.DateTimeField(null=True, blank=True)),
                (
                    "source",
                    models.CharField(
                        default=b"PHONE",
                        max_length=20,
                        choices=[
                            (b"PHONE", b"Phone"),
                            (b"VOICEMAIL", b"Voicemail"),
                            (b"SMS", b"Sms"),
                            (b"WEB", b"Web"),
                        ],
                    ),
                ),
                ("search_field", models.TextField(db_index=True, null=True, blank=True)),
                ("complaint_flag", models.BooleanField(default=False)),
                ("adaptation_details", models.ForeignKey(blank=True, to="legalaid.AdaptationDetails", null=True)),
            ],
            options={"permissions": (("run_reports", "Can run reports"),)},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="CaseKnowledgebaseAssignment",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("alternative_help_article", models.ForeignKey(to="knowledgebase.Article")),
                ("assigned_by", models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ("case", models.ForeignKey(to="legalaid.Case")),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="CaseNotesHistory",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("operator_notes", models.TextField(null=True, blank=True)),
                ("provider_notes", models.TextField(null=True, blank=True)),
                ("include_in_summary", models.BooleanField(default=True)),
                ("case", models.ForeignKey(to="legalaid.Case")),
                ("created_by", models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created",)},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("name", models.CharField(max_length=500)),
                ("code", models.CharField(unique=True, max_length=50)),
                ("raw_description", models.TextField(blank=True)),
                ("ecf_available", models.BooleanField(default=False)),
                ("mandatory", models.BooleanField(default=False)),
                ("description", models.TextField(editable=False, blank=True)),
                ("order", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["order"], "verbose_name_plural": "categories"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Deductions",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                (
                    "income_tax_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "income_tax_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                (
                    "income_tax",
                    cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True),
                ),
                (
                    "national_insurance_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "national_insurance_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                (
                    "national_insurance",
                    cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True),
                ),
                (
                    "maintenance_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "maintenance_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                (
                    "maintenance",
                    cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True),
                ),
                (
                    "childcare_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "childcare_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                (
                    "childcare",
                    cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True),
                ),
                (
                    "mortgage_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "mortgage_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                ("mortgage", cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True)),
                (
                    "rent_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "rent_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                ("rent", cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True)),
                ("criminal_legalaid_contributions", legalaid.fields.MoneyField(default=None, null=True, blank=True)),
            ],
            options={"abstract": False},
            bases=(core.cloning.CloneModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="EligibilityCheck",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("reference", uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ("your_problem_notes", models.TextField(blank=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "state",
                    models.CharField(
                        default=b"unknown",
                        max_length=50,
                        choices=[(b"unknown", b"Unknown"), (b"yes", b"Yes"), (b"no", b"No")],
                    ),
                ),
                (
                    "dependants_young",
                    models.PositiveIntegerField(
                        default=None, null=True, blank=True, validators=[django.core.validators.MaxValueValidator(50)]
                    ),
                ),
                (
                    "dependants_old",
                    models.PositiveIntegerField(
                        default=None, null=True, blank=True, validators=[django.core.validators.MaxValueValidator(50)]
                    ),
                ),
                ("on_passported_benefits", models.NullBooleanField(default=None)),
                ("on_nass_benefits", models.NullBooleanField(default=None)),
                ("specific_benefits", jsonfield.fields.JSONField(null=True, blank=True)),
                ("is_you_or_your_partner_over_60", models.NullBooleanField(default=None)),
                ("has_partner", models.NullBooleanField(default=None)),
                ("calculations", jsonfield.fields.JSONField(null=True, blank=True)),
                ("category", models.ForeignKey(blank=True, to="legalaid.Category", null=True)),
            ],
            options={"abstract": False, "ordering": ("-created",)},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Income",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                (
                    "earnings_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "earnings_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                ("earnings", cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True)),
                (
                    "self_employment_drawings_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "self_employment_drawings_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                (
                    "self_employment_drawings",
                    cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True),
                ),
                (
                    "benefits_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "benefits_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                ("benefits", cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True)),
                (
                    "tax_credits_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "tax_credits_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                (
                    "tax_credits",
                    cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True),
                ),
                (
                    "child_benefits_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "child_benefits_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                (
                    "child_benefits",
                    cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True),
                ),
                (
                    "maintenance_received_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "maintenance_received_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                (
                    "maintenance_received",
                    cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True),
                ),
                (
                    "pension_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "pension_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                ("pension", cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True)),
                (
                    "other_income_interval_period",
                    cla_common.money_interval.fields.MoneyIntervalAutoCharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        editable=False,
                        choices=[
                            (b"per_week", "per week"),
                            (b"per_2week", "2 weekly"),
                            (b"per_4week", "4 weekly"),
                            (b"per_month", "per month"),
                            (b"per_year", "per year"),
                        ],
                    ),
                ),
                (
                    "other_income_per_interval_value",
                    cla_common.money_interval.fields.MoneyIntervalAutoBigIntegerField(
                        null=True, editable=False, blank=True
                    ),
                ),
                (
                    "other_income",
                    cla_common.money_interval.fields.MoneyIntervalField(default=None, null=True, blank=True),
                ),
                ("self_employed", models.NullBooleanField(default=None)),
            ],
            options={"abstract": False},
            bases=(core.cloning.CloneModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="MatterType",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("code", models.CharField(max_length=4)),
                ("description", models.CharField(max_length=255)),
                (
                    "level",
                    models.PositiveSmallIntegerField(
                        choices=[(1, b"1"), (2, b"2")], validators=[django.core.validators.MaxValueValidator(2)]
                    ),
                ),
                ("category", models.ForeignKey(to="legalaid.Category")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MediaCode",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("code", models.CharField(max_length=20)),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MediaCodeGroup",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("name", models.CharField(max_length=128)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("deductions", models.ForeignKey(blank=True, to="legalaid.Deductions", null=True)),
                ("income", models.ForeignKey(blank=True, to="legalaid.Income", null=True)),
            ],
            options={"abstract": False, "ordering": ("-created",), "verbose_name_plural": "people"},
            bases=(core.cloning.CloneModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="PersonalDetails",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("title", models.CharField(max_length=20, null=True, blank=True)),
                ("full_name", models.CharField(max_length=400, null=True, blank=True)),
                ("postcode", models.CharField(max_length=12, null=True, blank=True)),
                ("street", models.CharField(max_length=255, null=True, blank=True)),
                ("mobile_phone", models.CharField(max_length=20, null=True, blank=True)),
                ("home_phone", models.CharField(max_length=20, blank=True)),
                ("email", models.EmailField(max_length=75, blank=True)),
                ("date_of_birth", models.DateField(null=True, blank=True)),
                ("ni_number", models.CharField(max_length=10, null=True, blank=True)),
                ("contact_for_research", models.NullBooleanField()),
                ("vulnerable_user", models.NullBooleanField()),
                (
                    "safe_to_contact",
                    models.CharField(
                        default=b"SAFE",
                        max_length=30,
                        null=True,
                        blank=True,
                        choices=[
                            (b"SAFE", b"Safe to contact"),
                            (b"DONT_CALL", b"Not safe to call"),
                            (b"NO_MESSAGE", b"Not safe to leave a message"),
                        ],
                    ),
                ),
                (
                    "safe_to_email",
                    models.CharField(
                        default=b"SAFE",
                        max_length=20,
                        null=True,
                        blank=True,
                        choices=[(b"SAFE", b"Safe to email"), (b"DONT_EMAIL", b"Not safe to email")],
                    ),
                ),
                ("case_count", models.PositiveSmallIntegerField(default=0)),
                ("reference", uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ("diversity", models.BinaryField(null=True, blank=True)),
                ("diversity_modified", models.DateTimeField(null=True, editable=False, blank=True)),
                ("search_field", models.TextField(db_index=True, null=True, blank=True)),
            ],
            options={"verbose_name_plural": "personal details"},
            bases=(core.cloning.CloneModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Property",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("value", legalaid.fields.MoneyField(default=None, null=True, blank=True)),
                ("mortgage_left", legalaid.fields.MoneyField(default=None, null=True, blank=True)),
                (
                    "share",
                    models.PositiveIntegerField(
                        default=None, null=True, blank=True, validators=[django.core.validators.MaxValueValidator(100)]
                    ),
                ),
                ("disputed", models.NullBooleanField(default=None)),
                ("main", models.NullBooleanField(default=None)),
                ("eligibility_check", models.ForeignKey(to="legalaid.EligibilityCheck")),
            ],
            options={"ordering": ("-created",), "verbose_name_plural": "properties"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Savings",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("bank_balance", legalaid.fields.MoneyField(default=None, null=True, blank=True)),
                ("investment_balance", legalaid.fields.MoneyField(default=None, null=True, blank=True)),
                ("asset_balance", legalaid.fields.MoneyField(default=None, null=True, blank=True)),
                ("credit_balance", legalaid.fields.MoneyField(default=None, null=True, blank=True)),
            ],
            options={"abstract": False},
            bases=(core.cloning.CloneModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ThirdPartyDetails",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("pass_phrase", models.CharField(max_length=255, null=True, blank=True)),
                (
                    "reason",
                    models.CharField(
                        default=b"",
                        max_length=30,
                        null=True,
                        blank=True,
                        choices=[
                            (b"CHILD_PATIENT", b"Child or patient"),
                            (b"POWER_ATTORNEY", b"Subject to power of attorney"),
                            (b"NO_TELEPHONE_DISABILITY", b"Cannot communicate via the telephone, due to disability"),
                            (
                                b"NO_TELEPHONE_LANGUAGE",
                                b"Cannot communicate via the telephone, due to a language requirement",
                            ),
                            (b"OTHER", b"Other"),
                        ],
                    ),
                ),
                (
                    "personal_relationship",
                    models.CharField(
                        max_length=30,
                        choices=[
                            (b"PARENT_GUARDIAN", b"Parent or guardian"),
                            (b"FAMILY_FRIEND", b"Family member or friend"),
                            (b"PROFESSIONAL", b"Professional"),
                            (b"LEGAL_ADVISOR", b"Legal adviser"),
                            (b"OTHER", b"Other"),
                        ],
                    ),
                ),
                ("personal_relationship_note", models.CharField(max_length=255, blank=True)),
                ("spoke_to", models.NullBooleanField()),
                ("no_contact_reason", models.TextField(null=True, blank=True)),
                ("organisation_name", models.CharField(max_length=255, null=True, blank=True)),
                ("reference", uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ("personal_details", models.ForeignKey(to="legalaid.PersonalDetails")),
            ],
            options={"abstract": False, "verbose_name_plural": "third party details"},
            bases=(core.cloning.CloneModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name="person",
            name="savings",
            field=models.ForeignKey(blank=True, to="legalaid.Savings", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="mediacode",
            name="group",
            field=models.ForeignKey(to="legalaid.MediaCodeGroup"),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(name="mattertype", unique_together=set([("code", "level")])),
        migrations.AddField(
            model_name="eligibilitycheck",
            name="disputed_savings",
            field=models.ForeignKey(blank=True, to="legalaid.Savings", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="eligibilitycheck",
            name="partner",
            field=models.ForeignKey(related_name="partner", blank=True, to="legalaid.Person", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="eligibilitycheck",
            name="you",
            field=models.ForeignKey(related_name="you", blank=True, to="legalaid.Person", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="case",
            name="alternative_help_articles",
            field=models.ManyToManyField(
                to="knowledgebase.Article", null=True, through="legalaid.CaseKnowledgebaseAssignment", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="case",
            name="created_by",
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="case",
            name="diagnosis",
            field=models.OneToOneField(
                null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to="diagnosis.DiagnosisTraversal"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="case",
            name="eligibility_check",
            field=models.OneToOneField(null=True, blank=True, to="legalaid.EligibilityCheck"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="case",
            name="from_case",
            field=models.ForeignKey(related_name="split_cases", blank=True, to="legalaid.Case", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="case",
            name="locked_by",
            field=models.ForeignKey(related_name="case_locked", blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="case",
            name="matter_type1",
            field=models.ForeignKey(related_name="+", blank=True, to="legalaid.MatterType", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="case",
            name="matter_type2",
            field=models.ForeignKey(related_name="+", blank=True, to="legalaid.MatterType", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="case",
            name="media_code",
            field=models.ForeignKey(blank=True, to="legalaid.MediaCode", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="case",
            name="personal_details",
            field=models.ForeignKey(blank=True, to="legalaid.PersonalDetails", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="case",
            name="provider",
            field=models.ForeignKey(blank=True, to="cla_provider.Provider", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="case",
            name="thirdparty_details",
            field=models.ForeignKey(blank=True, to="legalaid.ThirdPartyDetails", null=True),
            preserve_default=True,
        ),
    ]
