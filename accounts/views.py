from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Register a new user. Default role is 'customer'.
    Only administrators can register users with roles like 'admin' or 'theatre_manager'.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Register a new user",
        responses={
            201: UserSerializer,
            400: OpenApiResponse(description="Bad Request - Validation Errors")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = UserSerializer(user).data
        return Response(user_data, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(views.APIView):
    """
    Authenticate a user using username or email and return JWT access/refresh tokens.
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    @extend_schema(
        summary="User login (JWT)",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Successful authentication"),
            400: OpenApiResponse(description="Invalid credentials or bad request")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the logged-in user's profile details.
    """
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    @extend_schema(summary="Retrieve current user profile")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(summary="Update current user profile (full)")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(summary="Update current user profile (partial)")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ChangePasswordView(views.APIView):
    """
    Change the logged-in user's password.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    @extend_schema(
        summary="Change user password",
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password successfully changed"),
            400: OpenApiResponse(description="Validation errors (e.g. wrong old password)")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been changed successfully."}, status=status.HTTP_200_OK)
