from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from .models import Notification

User = get_user_model()


class NotificationAdminForm(forms.ModelForm):
    TARGET_CHOICES = [
        ('single', _("Single User")),
        ('all', _("All Users")),
        ('students', _("All UI Students")),
    ]

    target_group = forms.ChoiceField(
        choices=TARGET_CHOICES,
        label=_("Send to"),
        initial='single',
        help_text=_("Choose whether to send this notification to a single user, to all users, or to all UI students."),
    )

    class Meta:
        model = Notification
        fields = ['target_group', 'user', 'title', 'body', 'type', 'has_been_read']
        widgets = {
            'has_been_read': forms.CheckboxInput(attrs={'disabled': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['target_group'].initial = 'single'

        if 'user' in self.fields:
            self.fields['user'].required = False

    def clean(self):
        cleaned = super().clean()
        tg = cleaned.get('target_group')

        if tg == 'single':
            if not cleaned.get('user'):
                raise forms.ValidationError({
                    'user': _("You must select exactly one user when target is 'Single User'.")
                })
        return cleaned


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationAdminForm

    list_display = ('id', 'user', 'title', 'type', 'has_been_read', 'created_at')
    list_filter = ('has_been_read', 'created_at', 'type')
    search_fields = ('user__username', 'title', 'body')
    ordering = ('-created_at',)

    readonly_fields = ('has_been_read', 'created_at')

    fieldsets = (
        (None, {
            'fields': (
                'target_group',
                'user',
                'title',
                'body',
                'type',
                'has_been_read',
                'created_at',
            )
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """
        Always keep 'has_been_read' and 'created_at' readonly.
        When editing (obj is not None), also make 'user' readonly because we do not reassign after creation.
        """
        ro = list(self.readonly_fields)
        if obj:
            ro.append('user')
        return ro

    def save_model(self, request, obj, form, change):
        """
        Depending on the chosen target_group, create Notification(s):
          - single: standard save (obj.user must be set).
          - all: create one Notification per User (ignoring obj.user).
          - students: create one Notification per User where is_ui_student = True.
        """
        tg = form.cleaned_data.get('target_group')

        # If editing an existing Notification, just save changes to that one record
        if change:
            super().save_model(request, obj, form, change)
            self.message_user(request, _("Notification updated."), level=messages.SUCCESS)
            return

        title = form.cleaned_data['title']
        body = form.cleaned_data['body']
        ntype = form.cleaned_data['type']

        if tg == 'all':
            users = User.objects.all()
            with transaction.atomic():
                for u in users:
                    Notification.objects.create(
                        user=u,
                        title=title,
                        body=body,
                        type=ntype,
                        has_been_read=False,
                    )
            self.message_user(request, _("Notification sent to all users."), level=messages.SUCCESS)
            return

        if tg == 'students':
            users = User.objects.filter(is_ui_student=True)
            with transaction.atomic():
                for u in users:
                    Notification.objects.create(
                        user=u,
                        title=title,
                        body=body,
                        type=ntype,
                        has_been_read=False,
                    )
            self.message_user(request, _("Notification sent to all UI students."), level=messages.SUCCESS)
            return

        single_user = form.cleaned_data.get('user')

        if single_user:
            obj.user = single_user
            obj.has_been_read = False
            super().save_model(request, obj, form, change)
            self.message_user(request, _("Notification sent to %(username)s.") % {
                'username': single_user.username}, level=messages.SUCCESS)
        else:
            self.message_user(request, _("No user selected."), level=messages.ERROR)
