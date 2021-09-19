from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import CreateUserSerializer
from .swagger_utils import SwaggerAuthSerializer


class UserRegistration(CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [
        AllowAny,
    ]

    @swagger_auto_schema(
        request_body=CreateUserSerializer,
        responses={
            status.HTTP_201_CREATED: SwaggerAuthSerializer,
        },
    )
    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            account = serializer.save()
            user_info = {"token": Token.objects.get(user=account).key}
            return Response(data=user_info, status=201)
        return Response({"message": "Account could not be created"}, status=400)


class UserLogin(ObtainAuthToken):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: SwaggerAuthSerializer,
        },
    )
    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
