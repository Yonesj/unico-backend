from django.db import models


class Faculty(models.Model):
    name = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Faculties"

    def __str__(self):
        return self.name
