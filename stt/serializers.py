from rest_framework import serializers
from stt.models import STTResult


class STTSerializer(serializers.ModelSerializer):
    class Meta:
        model = STTResult
        fields = "__all__"

