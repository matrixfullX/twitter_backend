from django.core.exceptions import BadRequest
from django.contrib.auth import authenticate
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView

from apps.authentication import serializers
from apps.authentication.social_login import register_user_with_social_account
from apps.authentication.tokens import get_tokens_for_user
from apps.utils.response import res


class GoogleLoginView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        request_body=serializers.GoogleLoginSerializer,
        operation_id="Login with Google",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="User successfully logged in",
                examples={
                    "application/json": {
                        "message": res["LOGIN_SUCCESS"],
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QxMjM0NTY3IiwiaWF0IjoxNjY4MDIyMDQ1LCJleHAiOjE2NjgyMjIwNDV9.0ySjxP4kYn0SbZ9jyX8tT9wZ5Gc2yq0fZw6aQOQjZ0"
                    }
                }
            )
        }
    )
    def post(self, request) -> Response:
        serializer = serializers.GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            data = register_user_with_social_account(**serializer.validated_data)
        except BadRequest as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_200_OK)


class SignupView(viewsets.ModelViewSet):
    permission_classes = []
    serializer_class = serializers.SignupSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs) -> Response:
        serializer = serializers.SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": res["SUCCESSFUL_REGISTRATION"]},
            status=status.HTTP_201_CREATED,
        )


class LoginView(viewsets.ModelViewSet):
    permission_classes = []
    serializer_class = serializers.LoginSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get("email")
            password = serializer.data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                user.last_login = timezone.now()
                user.save()
                token = get_tokens_for_user(user)
                return Response(
                    {"message": res["LOGIN_SUCCESS"], "token": token},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"errors": res["EMAIL_OR_PASSWORD_IS_NOT_VALID"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserChangePasswordView(viewsets.ModelViewSet):
    serializer_class = serializers.UserChangePasswordSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = serializers.UserChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"message": res["PASSWORD_CHANGED_SUCCESSFULLY"]},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(viewsets.ModelViewSet):
    permission_classes = []
    serializer_class = serializers.LogoutSerializer
    http_method_names = ["post"]
    lookup_field = "public_id"

    def create(self, request, *args, **kwargs):
        serializer = serializers.LogoutSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"message": res["LOGOUT_SUCCESSFULLY"]},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
