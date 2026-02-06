from django.shortcuts import render
from rest_framework  import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from .models import User
from .serializers import RegisterSerializer, ProfileSerializer, MyTokenObtainPairSerializer
from activitylog.models import ActivityLog

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


    def perform_create(self, serializer):
        user = serializer.save()

        ActivityLog.objects.create(
            user=user,
            action = 'REGISTER',
            description = f'{user.username} registered as {user.role}'
        )

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    


# class LoginView(generics.GenericAPIView):
#     serializer_class = [LoginSerializer]
#     permission_classes = [permissions.AllowAny]

    
#     def post(self, request):
#         user = self.get_serializer(data=request.data)
#         user.is_valid(raise_exception=True)
#         user = user.validated_data

#         refresh = RefreshToken.for_user(user)

#         return Response({
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         })
    

class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    


# class AdminUserView(generics.ListAPIView):
#     serializer_class = ProfileSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         if self.request.user != 'ADMIN':
#             return User.objects.none()
#         return User.objects.all()


