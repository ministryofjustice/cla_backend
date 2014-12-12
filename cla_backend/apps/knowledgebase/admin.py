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


class ArticleCategoryMatrixAdmin(admin.ModelAdmin):
    list_display = (
        'preferred_signpost',
        'category_name',
        'service_name',)
    list_editable = ('preferred_signpost',)
    list_display_links = ('service_name',)
    ordering = (
        'article_category__name',
        '-preferred_signpost',
        'article__service_name')

    def service_name(self, obj):
        return obj.article.service_name

    def category_name(self, obj):
        return obj.article_category.name


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleCategoryMatrix, ArticleCategoryMatrixAdmin)
