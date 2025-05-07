from django.utils import timezone
from django.contrib import admin
from src.reviews.models import Review, State


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'created_at', 'state')
    list_filter = ('state', 'created_at', 'would_take_again', 'attendance_policy')
    search_fields = ('user__username', 'course__name', 'review_text')
    ordering = ('-created_at',)
    readonly_fields = ('validated_by', 'validated_at', 'created_at')
    actions = ['approve_reviews', 'reject_reviews']

    fieldsets = (
        (None, {
            'fields': ('user', 'course', 'created_at')
        }),
        ("Ratings & Evaluation", {
            'fields': (
                'grading',
                'exam_difficulty',
                'general_knowledge',
                'homework_difficulty',
                'teaching_engagement',
                'received_score',
                'would_take_again',
            )
        }),
        ("Additional Info", {
            'fields': ('attendance_policy', 'exam_resources', 'review_text')
        }),
        ("Moderation", {
            'fields': ('state', 'validated_by', 'validated_at')
        }),
    )

    def get_queryset(self, request):
        return self.model.all_objects.select_related('user', 'course')

    def save_model(self, request, obj, form, change):
        if change and 'state' in form.changed_data:
            obj.validated_by = request.user
            obj.validated_at = timezone.now()
        super().save_model(request, obj, form, change)

    @admin.action(description="Mark selected reviews as approved")
    def approve_reviews(self, request, queryset):
        updated = queryset.update(state=State.APPROVED, validated_by=request.user, validated_at=timezone.now())
        self.message_user(request, f"{updated} review(s) marked as approved.")

    @admin.action(description="Mark selected reviews as rejected")
    def reject_reviews(self, request, queryset):
        updated = queryset.update(state=State.REJECTED, validated_by=request.user, validated_at=timezone.now())
        self.message_user(request, f"{updated} review(s) marked as rejected.")
