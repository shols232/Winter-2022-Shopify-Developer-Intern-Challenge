from rest_framework import serializers
from rest_framework.fields import UUIDField


class SwaggerAuthSerializer(serializers.Serializer):
    token = UUIDField()