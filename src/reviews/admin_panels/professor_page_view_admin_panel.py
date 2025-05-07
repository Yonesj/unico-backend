from django.contrib import admin
from src.reviews.models import ProfessorPageView


@admin.register(ProfessorPageView)
class ProfessorPageViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'professor', 'ip_address', 'viewed_at', 'user_agent_short')
    list_filter = ['viewed_at']
    search_fields = ('professor__first_name', 'professor__last_name', 'ip_address', 'user_agent')
    ordering = ('-viewed_at',)
    readonly_fields = ('professor', 'viewed_at', 'ip_address', 'user_agent')

    fieldsets = (
        (None, {
            'fields': ('professor', 'viewed_at', 'ip_address', 'user_agent')
        }),
    )

    def user_agent_short(self, obj):
        return (obj.user_agent[:50] + '...') if obj.user_agent and len(obj.user_agent) > 50 else obj.user_agent

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    user_agent_short.short_description = "User Agent"
