from django.db import models


class ProfessorPageView(models.Model):
    """
    Logs every time someone (anonymous or authenticated) views
    a Professor detail page, without requiring a User FK.
    """
    professor  = models.ForeignKey('Professor', on_delete=models.CASCADE, related_name='page_views', db_index=True)
    viewed_at  = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=256, blank=True)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        who = self.ip_address or "unknown"
        return f"View of {self.professor} by {who} at {self.viewed_at}"
