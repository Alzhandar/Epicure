from rest_framework import serializers

class ChatSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
