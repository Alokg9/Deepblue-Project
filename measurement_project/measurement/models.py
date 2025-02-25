
from django.db import models
from django.contrib.auth.models import User

class CalibrationData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pixels_per_cm = models.FloatField()
    reference_object_size = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class Measurement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dimensions = models.JSONField()
    mode = models.CharField(max_length=20)
    additional_data = models.JSONField(null=True, blank=True)
    image = models.ImageField(upload_to='measurements/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
