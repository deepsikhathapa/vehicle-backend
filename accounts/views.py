from django.shortcuts import render
from rest_framework  import generics, permissions, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from .models import User
from .serializers import RegisterSerializer, ProfileSerializer, MyTokenObtainPairSerializer
from activitylog.models import ActivityLog
from rest_framework.decorators import action
from django.utils import timezone

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


    def perform_create(self, serializer):
        user = serializer.save()
        print(f"User created: {user.id} - {user.username}")

        ActivityLog.objects.create(
            user=user,
            action = 'REGISTER',
            description = f'{user.username} registered as {user.role}'
        )

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
    


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


class UserView(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'])
    def vendors(self, request):
        """Get list of all vendors (for customers to browse)"""
        vendors = User.objects.filter(role=User.VENDOR)
        serializer = self.get_serializer(vendors, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def customers(self, request):
        """Get list of all customers (for vendors to browse)"""
        customers = User.objects.filter(role='CUSTOMER')
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def set_online_status(self, request):
        """Update user's online status"""
        is_online = request.data.get('is_online', False)
        request.user.is_online = is_online
        if not is_online:
            request.user.last_seen = timezone.now()
        request.user.save()
        return Response({'status': 'online status updated'})





