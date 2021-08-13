from django.contrib import admin
from .models import CTIPMain


class CTIPMainAdmin(admin.ModelAdmin):
    """Admin back end for Geo data management."""

    search_fields = ['case_number']
    list_display = ['case_id', 'case_number', 'get_creator']
    # readonly_fields = ['area_id']
    list_filter = ['is_void', 'case__created_by']

    def get_creator(self, obj):
        return obj.case.created_by
    get_creator.short_description = 'Creator'
    get_creator.admin_order_field = 'case__created_by'
    # actions = [dump_to_csv]


admin.site.register(CTIPMain, CTIPMainAdmin)
