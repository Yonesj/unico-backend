from django.contrib import admin
from src.reviews.models import ReviewReaction


@admin.register(ReviewReaction)
class ReviewReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'review__course', 'value', 'created_at')
    list_filter = ('value', 'created_at')
    search_fields = ('user__username', 'review__id', 'review__course__name')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'review', 'value', 'created_at')

    fieldsets = (
        (None, {
            'fields': ('user', 'review', 'value', 'created_at')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
