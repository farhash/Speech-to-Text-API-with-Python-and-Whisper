from rest_framework import serializers
from stt.models import STTResult
from django.contrib.auth import get_user_model


User = get_user_model()

class STTSerializer(serializers.ModelSerializer):
    class Meta:
        model = STTResult
        fields = "__all__"

