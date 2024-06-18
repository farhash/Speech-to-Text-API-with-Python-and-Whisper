from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()

class STTResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stt_result", null=True, blank=True)
    stt_result_key = models.CharField(unique=True, max_length=120)
    stt_result_status = models.CharField(max_length=50, blank=True, null=False, default="pending")
    stt_result_script = models.TextField(blank=True, null=True)
    stt_start_time = models.DateTimeField(blank=True, null=False, default=timezone.now)
    stt_end_time = models.DateTimeField(blank=True, null=False, default=timezone.now)
    audio_source_url = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "stt_result"

    def __str__(self):
        return self.stt_result_key

class upload_audio(models.Model):
    upload_time = models.DateTimeField(blank=True, null=False, default=timezone.now)
    audio = models.FileField(upload_to= 'uploaded/%Y/%m/%d/', null=False)
    class Meta:
        db_table = "uploaded_files"