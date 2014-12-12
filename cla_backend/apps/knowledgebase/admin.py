from django.contrib import admin

from .models import Article, ArticleCategoryMatrix


class ArticleCategoryMatrixInline(admin.TabularInline):
    model = ArticleCategoryMatrix


class ArticleAdmin(admin.ModelAdmin):
    actions = None
    inlines = [ArticleCategoryMatrixInline]
    ordering = ['service_name']

    fields = (
        'resource_type', 'service_name', 'organisation', 'website',
        'description', 'how_to_use', 'when_to_use', 'address', 'helpline',
        'opening_hours', 'keywords', 'geographic_coverage',
        'type_of_service', 'accessibility'
    )
    list_display = (
        'service_name', 'resource_type'
    )
    search_fields = [
        'service_name', 'organisation', 'description', 'how_to_use',
        'when_to_use', 'keywords', 'type_of_service'
    ]


admin.site.register(Article, ArticleAdmin)
