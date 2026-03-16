from rest_framework import serializers

from .models import Decree

from rest_framework import serializers
from .models import Decree


class DecreeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Decree
        fields = ['id', 'number', 'date_of_issue', 'scan_ru', 'scan_ky', 'aplication']


class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    application_id = serializers.IntegerField()

