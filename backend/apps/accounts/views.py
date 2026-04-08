from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, MeSerializer, RegisterSerializer, RoleSerializer, UpdateProfileSerializer

User = get_user_model()


def generate_user_tokens(user):
    token = RefreshToken.for_user(user)
    return {
        "refresh_token":str(token),
        "access_token":str(token.access_token),
        "user":MeSerializer(user).data
    }



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(generate_user_tokens(user), status=status.HTTP_201_CREATED)
    



class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        
        return Response(generate_user_tokens(user), status=status.HTTP_200_OK)
    



class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        serializer = UpdateProfileSerializer(
            instance=request.user,
            data=request.data,
            context={"request":request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(MeSerializer(request.user).data, status=status.HTTP_200_OK)
    



class RoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(user=request.user)
        return Response({"user": MeSerializer(user).data}, status=status.HTTP_200_OK)