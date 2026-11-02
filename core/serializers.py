from rest_framework import serializers
from .models import Machine, Manual, QuestionRecord


class MachineSerializer(serializers.ModelSerializer):

  class Meta:
    model = Machine
    fields = ['id', 'machine_id', 'name', 'description']


class ManualUploadSerializer(serializers.ModelSerializer):

  class Meta:
    model = Manual
    fields = ['id', 'machine', 'title', 'revision', 'pdf_file']


class QuerySerializer(serializers.Serializer):
  machine_id = serializers.CharField(max_length=50)
  query = serializers.CharField(max_length=1000)


class QuestionRecordSerializer(serializers.ModelSerializer):
  machine_id = serializers.CharField(source='machine.machine_id', read_only=True)
  username = serializers.CharField(source='user.username', read_only=True)

  class Meta:
    model = QuestionRecord
    fields = [
        'id',
        'username',
        'machine_id',
        'query',
        'answer',
        'sources',
        'status',
        'timestamp',
    ]
    