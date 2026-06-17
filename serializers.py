from rest_framework import serializers # pyright: ignore[reportMissingImports]
from .models import IMSVoiceRecord, CDRRule

class IMSVoiceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = IMSVoiceRecord
        fields = '__all__'

class CDRRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDRRule
        fields = '__all__'