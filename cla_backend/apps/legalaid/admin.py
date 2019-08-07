from django.contrib import admin

from .models import (
    Category,
    Case,
    EligibilityCheck,
    PersonalDetails,
    Property,
    Person,
    EODDetails,
    EODDetailsCategory,
    MatterType,
    ContactResearchMethod,
)

from .admin_support.forms import CategoryModelForm


class CategoryModelAdmin(admin.ModelAdmin):
    form = CategoryModelForm


class EODDetailsCategoryAdmin(admin.TabularInline):
    model = EODDetailsCategory
    readonly_fields = ("category", "is_major")
    extra = 0


class EODDetailsAdmin(admin.ModelAdmin):
    inlines = (EODDetailsCategoryAdmin,)


class CaseAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "eligibility_check",
        "diagnosis",
        "personal_details",
        "thirdparty_details",
        "adaptation_details",
        "from_case",
    )
    readonly_fields = ("callback_window_type",)

    def get_fields(self, request, obj=None, **kwargs):
        fields = super(CaseAdmin, self).get_fields(request, obj, **kwargs)
        fields = self.move_field_after("callback_window_type", "requires_action_at", fields)
        return fields

    @staticmethod
    def move_field_after(field_to_move, target_field, fields):
        if field_to_move in fields and target_field in fields:
            field_to_move_index = fields.index(field_to_move)
            target_field_index = fields.index(target_field)
            fields.insert(target_field_index + 1, fields.pop(field_to_move_index))
        return fields


admin.site.register(Category, CategoryModelAdmin)
# admin.site.register(Question)
# admin.site.register(Answer)
admin.site.register(Case, CaseAdmin)
admin.site.register(EligibilityCheck)
admin.site.register(PersonalDetails)
admin.site.register(Property)
admin.site.register(Person)
admin.site.register(EODDetails, EODDetailsAdmin)
admin.site.register(MatterType)
admin.site.register(ContactResearchMethod)
