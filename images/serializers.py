from typing import Dict

from images.models import UserImage
from lib.validators import validate_image_extension, validate_image_file_size
from rest_framework import serializers
from rest_framework.fields import CharField


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True, validators=[validate_image_file_size, validate_image_extension])
    name = serializers.CharField(source="image.name", read_only=True)
    owner = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = UserImage
        fields = ["owner", "image", "name", "times_shared", "size"]
        extra_kwargs = {'size': {'read_only': True}, 'times_shared': {'read_only': True}}


class ShareImageSerializer(serializers.Serializer[Dict[str, str]]):
    target_user = CharField()
    image_name = CharField()
