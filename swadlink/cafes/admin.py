from django.contrib import admin
from .models import Cafe, City, State
from django import forms
from django.utils import timezone
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

    list_display = ('name', 'slug', 'phone', 'email', 'get_owners', 'date_joined', 'is_active', 'messages_this_month')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'phone', 'email')
    ordering = ('-date_joined',)

    def messages_this_month(self, obj):
        now = timezone.now()
        return MessageLog.objects.filter(
            cafe=obj,
            sent_at__year=now.year,
            sent_at__month=now.month
        ).count()
        messages_this_month.short_description = "Messages (This Month)"

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


# admin.py


from .models import MessageLog

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['cafe', 'message_type', 'sent_at']
    list_filter = ['cafe', 'message_type', 'sent_at']
    search_fields = ['cafe__name', 'content']
