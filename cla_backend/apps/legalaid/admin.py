from django.contrib import admin

from .models import Category, Case, EligibilityCheck, PersonalDetails, \
    Property, Finance


admin.site.register(Category)
# admin.site.register(Question)
# admin.site.register(Answer)
admin.site.register(Case)
admin.site.register(EligibilityCheck)
admin.site.register(PersonalDetails)
admin.site.register(Property)
admin.site.register(Finance)
