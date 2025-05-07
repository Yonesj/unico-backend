from django.db import models


class Course(models.Model):
    faculty    = models.ForeignKey('Faculty', null=True, on_delete=models.SET_NULL, related_name='courses')
    professor  = models.ForeignKey('Professor', on_delete=models.CASCADE, related_name='courses')
    name       = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('professor', 'name')

    def __str__(self):
        return self.name
