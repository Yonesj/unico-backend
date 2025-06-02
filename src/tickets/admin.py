from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html

from .models import Ticket, Message, TicketStatus
from src.notifications.models import Notification


class MessageInline(admin.TabularInline):
    model = Message
    fields = ('user', 'body', 'created_at')
    readonly_fields = ('user', 'body', 'created_at')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user_link',
        'status',
        'subject',
        'unit',
        'created_at_formatted',
        'updated_at_formatted',
        'message_count'
    )
    list_filter = ('status', 'subject', 'unit', 'created_at', 'updated_at')
    search_fields = ('title', 'user__username', 'user__email', 'uid__iexact')
    readonly_fields = ('uid', 'created_at', 'updated_at', 'user_display_info')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('title', 'user_display_info', 'uid')
        }),
        (_('Categorization & Status'), {
            'fields': ('subject', 'unit', 'status')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    inlines = [MessageInline] # Show messages related to this ticket
    actions = ['mark_as_closed', 'mark_as_open', 'mark_as_answered']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('messages')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if change and 'status' in form.changed_data and obj.status != TicketStatus.OPEN:
            verb = "بسته شد." if obj.status == TicketStatus.CLOSED else "پاسخ داده شد."

            Notification.objects.create(
                user=obj.user,
                title="تیکت",
                body=f"تیکت {obj.title}" + verb
            )


    def user_link(self, obj):
        if obj.user:
            link = reverse("admin:accounts_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', link, obj.user.get_username())
        return "-"

    def user_display_info(self, obj):
        if obj.user:
            return f"{obj.user.get_username()} (ID: {obj.user.id})"
        return _("No associated user")

    def created_at_formatted(self, obj):
        if obj.created_at:
            return obj.created_at.strftime("%Y-%m-%d %H:%M")
        return "-"

    def updated_at_formatted(self, obj):
        if obj.updated_at:
            return obj.updated_at.strftime("%Y-%m-%d %H:%M")
        return "-"

    def message_count(self, obj):
        return obj.messages.count()

    def mark_as_closed(self, request, queryset):
        updated_count = queryset.update(status=TicketStatus.CLOSED)
        self.message_user(request, _(f'{updated_count} tickets were marked as closed.'))

    def mark_as_open(self, request, queryset):
        updated_count = queryset.update(status=TicketStatus.OPEN)
        self.message_user(request, _(f'{updated_count} tickets were marked as Open.'))

    def mark_as_answered(self, request, queryset):
        updated_count = queryset.update(status=TicketStatus.ANSWERED)
        self.message_user(request, _(f'{updated_count} tickets were marked as Answered.'))

    user_link.short_description = _('User')
    user_link.admin_order_field = 'user__username'
    user_display_info.short_description = _('Ticket Creator')
    created_at_formatted.short_description = _('Created At')
    created_at_formatted.admin_order_field = 'created_at'
    updated_at_formatted.short_description = _('Updated At')
    updated_at_formatted.admin_order_field = 'updated_at'
    message_count.short_description = _('Messages')
    mark_as_closed.short_description = _("Mark selected tickets as Closed")
    mark_as_answered.short_description = _("Mark selected tickets as Answered")
    mark_as_open.short_description = _("Mark selected tickets as Open")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('ticket_link', 'user_link', 'short_body', 'created_at_formatted')
    list_filter = ('created_at',)
    search_fields = ('body', 'user__username', 'ticket__title', 'ticket__uid__iexact')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    fields = ('ticket', 'user', 'body', 'created_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket', 'user')

    def ticket_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.ticket:
            link = reverse("admin:tickets_ticket_change", args=[obj.ticket.id]) # Replace 'tickets' with your app_label
            return format_html('<a href="{}">{}</a>', link, obj.ticket.title[:50] + "...")
        return "-"

    ticket_link.short_description = _('Ticket')
    ticket_link.admin_order_field = 'ticket__title'

    def user_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.user:
            link = reverse("admin:accounts_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', link, obj.user.get_username())
        return "-"

    user_link.short_description = _('User')
    user_link.admin_order_field = 'user__username'

    def short_body(self, obj):
        return (obj.body[:75] + '...') if len(obj.body) > 75 else obj.body

    short_body.short_description = _('Body')

    def created_at_formatted(self, obj):
        if obj.created_at:
            return obj.created_at.strftime("%Y-%m-%d %H:%M")
        return "-"

    created_at_formatted.short_description = _('Created At')
    created_at_formatted.admin_order_field = 'created_at'

    def has_change_permission(self, request, obj=None):
        return False
