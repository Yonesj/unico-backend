import secrets

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from djoser.email import ActivationEmail
from django.utils import timezone
from django.template.loader import render_to_string

from .models import ActivationCode


class CustomActivationEmail(ActivationEmail):
    template_name = "emails/user_activation_email.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = self.context.get("user")

        if not user:
            raise ValueError("User context is missing in activation email.")

        activation_obj, created = ActivationCode.objects.get_or_create(user=user)

        if created or not activation_obj.code:
            activation_obj.code = secrets.token_hex(4).upper()  # 8-character code
            activation_obj.created_at = timezone.now()
            activation_obj.save(update_fields=['code', 'created_at'])

        context['activation_code'] = activation_obj.code
        context['username'] = user.username
        context['body'] = f"Hello {user.username}, your activation code is {activation_obj.code}"
        return context

    def send(self, to, *args, **kwargs):
        context = self.get_context_data()

        subject = "اکانت خود را فعال کنید"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = to if isinstance(to, list) else [to]

        html_content = render_to_string(self.template_name, context)
        text_content = context.get('body')

        email_message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()
