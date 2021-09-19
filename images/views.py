from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from images.serializers import ImageSerializer, ShareImageSerializer

from .models import UserImage


class AddImageView(APIView):
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, )

    @swagger_auto_schema(
        request_body=ImageSerializer,
        responses={
            status.HTTP_201_CREATED: ImageSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        files = request.FILES.getlist("image")
        images = []
        private = request.data.get("private")

        if not files:
            raise ValidationError("You must include at least one image.")

        for file in files:
            # determine upload type. private or public.
            data = {"image": file}
            if private:
                data["private"] = True

            serializer = self.serializer_class(data=data)

            if serializer.is_valid(raise_exception=True):
                serializer.save(owner=request.user)
                images.append(serializer.data)
            else:
                return Response({"message": "An Error Occured!"}, status=400)
        return Response(images, status=status.HTTP_201_CREATED)


class ListImageView(APIView):
    """Get a list of user owned images"""

    model = UserImage
    serializer_class = ImageSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: ImageSerializer(many=True),
        },
    )
    def get(self, request: Request, *args, **kwargs):
        objects = self.model.objects.filter(owner=request.user)
        serializer = self.serializer_class(objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SearchImagesView(APIView):
    """Search for images by name."""

    model = UserImage
    serializer_class = ImageSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "name",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            status.HTTP_201_CREATED: ImageSerializer(many=True),
        },
    )
    def get(self, request: Request) -> Response:
        image_name = request.GET.get("name")
        if not image_name:
            return Response(
                {"message": "A name parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Grab images all images, then filter by name and including images that are NOT private unless,
        # the private image owned by the requesting user.
        objects = self.model.objects.filter(
            Q(image__icontains=image_name) & (Q(owner=request.user) | Q(private=False))
        )
        serializer = self.serializer_class(objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShareImageView(APIView):
    """Transfer an image from the owner to a targeted user."""

    serializer_class = ShareImageSerializer

    @swagger_auto_schema(
        request_body=ShareImageSerializer,
        responses={
            status.HTTP_200_OK: "",
        },
    )
    def post(self, request: Request) -> Response:

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate data

        target_user = serializer.validated_data["target_user"]
        image_name = serializer.validated_data["image_name"]

        target_user = get_object_or_404(User, username=target_user)

        # Attempt to get an image by the name which also belongs to the requsting user.
        owner_image = get_object_or_404(UserImage, owner=request.user, image=image_name)

        # User should not be able to share an image to themselves
        if owner_image.owner == target_user:
            return Response(
                {
                    "message": "Unfortunately, you are not allowed to share images to yourself, that would be weird."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        target_user_has_image = UserImage.objects.filter(
            owner=target_user, image=owner_image.image
        ).exists()

        if target_user_has_image:
            return Response(
                {
                    "message": "Sorry, but this user already has this image. Try another one."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Create a new UserImage object for the to_user so he now has the image.
        UserImage.objects.create(owner=target_user, image=owner_image.image)

        # Increment times_shared for the image instance of the image owner by 1
        owner_image.times_shared += 1
        owner_image.save(update_fields=["times_shared"])

        message = "{} has been succesfully shared to {}".format(image_name, target_user)
        return Response({"message": message}, status=status.HTTP_200_OK)
