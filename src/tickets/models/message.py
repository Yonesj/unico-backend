from django.contrib.auth import get_user_model
from django.db import models


class Message(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    body = models.CharField(max_length=350)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"پاسخ از {self.user.username} به تیکت: {self.ticket.title[:30]}..."
