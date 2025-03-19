from django.contrib import admin
from .models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'position')
    list_editable = ('position',)
    search_fields = ('name',)
    ordering = ('position', 'name')
    
    def get_changelist_form(self, request, **kwargs):
        form = super().get_changelist_form(request, **kwargs)
        form.base_fields['position'].required = False
        return form