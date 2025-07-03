from django.contrib import admin
from .models import Cafe, City, State
from django import forms

class CafeAdminForm(forms.ModelForm):
    class Meta:
        model = Cafe
        fields = '__all__'

    # Make owners field not required in admin
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owners'].required = False


@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    form = CafeAdminForm

    list_display = ('name', 'slug', 'phone', 'email', 'get_owners', 'date_joined')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'phone', 'email')
    ordering = ('-date_joined',)

    def get_owners(self, obj):
        return ", ".join([owner.username for owner in obj.owners.all()])
    get_owners.short_description = 'Owners'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if change and obj.owners.count() == 0:
            from django.contrib import messages
            messages.warning(request, f"Café '{obj.name}' has no owners assigned.")
admin.site.register(City)
admin.site.register(State)