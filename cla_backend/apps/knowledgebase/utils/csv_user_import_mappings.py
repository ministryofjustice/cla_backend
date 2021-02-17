from knowledgebase.models import ArticleCategory


def transform_category(value):
    try:
        return ArticleCategory.objects.get(name=value)
    except ArticleCategory.DoesNotExist:
        raise ValueError("Could not find category with name: %s" % value)


def transform_preferred_signpost(value):
    value_normalised = value.lower()
    if value_normalised not in ["true", "false"]:
        raise ValueError("%s is an invalid value for Preferred signpost" % value)
    return value_normalised == "true"


TELEPHONE_COLUMN_FIELD_MAPPING = [
    [(19, "name"), (20, "number")],
    [(21, "name"), (22, "number")],
    [(23, "name"), (24, "number")],
    [(25, "name"), (26, "number")],
]

ARTICLE_COLUMN_FIELD_MAPPING = [
    (0, "pk"),
    (1, "created"),
    (2, "modified"),
    (3, "resource_type"),
    (4, "service_name"),
    (5, "service_tag"),
    (6, "organisation"),
    (7, "website"),
    (8, "email"),
    (9, "description"),
    (10, "public_description"),
    (11, "how_to_use"),
    (12, "when_to_use"),
    (13, "address"),
    (14, "opening_hours"),
    (15, "keywords"),
    (16, "geographic_coverage"),
    (17, "type_of_service"),
    (18, "accessibility"),
]

ARTICLE_CATEGORY_MATRIX_COLUMN_FIELD_MAPPING = [
    [(27, "article_category", transform_category), (28, "preferred_signpost", transform_preferred_signpost)],
    [(29, "article_category", transform_category), (30, "preferred_signpost", transform_preferred_signpost)],
    [(31, "article_category", transform_category), (32, "preferred_signpost", transform_preferred_signpost)],
    [(33, "article_category", transform_category), (34, "preferred_signpost", transform_preferred_signpost)],
    [(35, "article_category", transform_category), (36, "preferred_signpost", transform_preferred_signpost)],
    [(37, "article_category", transform_category), (38, "preferred_signpost", transform_preferred_signpost)],
]
