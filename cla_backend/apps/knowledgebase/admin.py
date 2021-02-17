from django.contrib import admin
from django.shortcuts import render
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseRedirect
from django.contrib import messages
from .models import Article, ArticleCategoryMatrix, TelephoneNumber
from .forms import KnowledgebaseCSVUploadForm


class TelephoneNumberInline(admin.TabularInline):
    model = TelephoneNumber


class ArticleCategoryMatrixInline(admin.TabularInline):
    model = ArticleCategoryMatrix


class ArticleAdmin(admin.ModelAdmin):
    change_list_template = "admin/knowledgebase/custom_change_list.html"
    actions = None
    inlines = [TelephoneNumberInline, ArticleCategoryMatrixInline]
    ordering = ["service_name"]

    fields = (
        "resource_type",
        "service_name",
        "service_tag",
        "organisation",
        "website",
        "email",
        "description",
        "public_description",
        "how_to_use",
        "when_to_use",
        "address",
        "opening_hours",
        "keywords",
        "geographic_coverage",
        "type_of_service",
        "accessibility",
    )
    list_display = ("service_name", "resource_type")
    search_fields = [
        "service_name",
        "organisation",
        "description",
        "how_to_use",
        "when_to_use",
        "keywords",
        "type_of_service",
    ]

    def get_urls(self):
        urls = super(ArticleAdmin, self).get_urls()
        my_urls = patterns(
            "", url(r"^import-csv/$", self.admin_site.admin_view(self.import_csv), name="knowledgebase_import_csv")
        )
        return my_urls + urls

    def import_csv(self, request):
        if not self.has_change_permission(request):
            raise PermissionDenied

        form = KnowledgebaseCSVUploadForm()
        if request.method == "POST":
            form = KnowledgebaseCSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, "CSV Imported successfully")
                return HttpResponseRedirect(
                    reverse("admin:%s_%s_changelist" % (self.model._meta.app_label, self.model._meta.model_name))
                )
        return render(request, "admin/knowledgebase/csv-upload.html", {"form": form})


class ArticleCategoryMatrixAdmin(admin.ModelAdmin):
    list_display = ("service_name", "category_name", "preferred_signpost")
    actions = None
    list_editable = ("preferred_signpost",)
    list_display_links = ("service_name",)
    search_fields = ["article_category__name", "article__service_name"]
    ordering = ("article_category__name", "-preferred_signpost", "article__service_name")

    def service_name(self, obj):
        return obj.article.service_name

    def category_name(self, obj):
        return obj.article_category.name


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleCategoryMatrix, ArticleCategoryMatrixAdmin)
