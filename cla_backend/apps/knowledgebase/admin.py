from django.contrib import admin

from .models import Article, ArticleCategory, ArticleCategoryMatrix


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


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleCategory)
admin.site.register(ArticleCategoryMatrix)
