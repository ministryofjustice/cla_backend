from django.contrib import admin

from .models import Category, Case, EligibilityCheck, PersonalDetails, \
    Property, Person, CaseLog, CaseLogType

from .admin_support.forms import CategoryModelForm


class CategoryModelAdmin(admin.ModelAdmin):
    form = CategoryModelForm


admin.site.register(Category, CategoryModelAdmin)
# admin.site.register(Question)
# admin.site.register(Answer)
admin.site.register(Case)
admin.site.register(EligibilityCheck)
admin.site.register(PersonalDetails)
admin.site.register(Property)
admin.site.register(Person)
admin.site.register(CaseLog)
admin.site.register(CaseLogType)
