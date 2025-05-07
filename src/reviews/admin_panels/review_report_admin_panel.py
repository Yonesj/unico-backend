from django.contrib import admin
from django.utils.html import format_html

from src.reviews.models import ReviewReport


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'review_link', 'reason', 'reported_at')
    list_filter = ('reason', 'reported_at')
    search_fields = (
        'reporter__username',
        'review__review_text',
        'review__course__name',
    )
    ordering = ['-reported_at']
    raw_id_fields = ('reporter', 'review')
    readonly_fields = ('reporter', 'review', 'reason', 'reported_at')

    fieldsets = (
        (None, {
            'fields': ('reporter', 'review_link', 'reason', 'reported_at')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def review_link(self, obj):
        url = f"/admin/reviews/review/{obj.review.pk}/change/"
        return format_html('<a href="{}">Review #{}</a>', url, obj.review.pk)

    review_link.short_description = "Review"
