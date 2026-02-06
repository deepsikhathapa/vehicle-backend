from rest_framework import generics, status, permissions
from rest_framework.response import Response

from .models import User
from .serializers import AdminSerializer
from .permissions import IsAdmin
from activitylog.models import ActivityLog


class AdminListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class AdminCostumerListView(generics.ListAPIView):
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


    def get_queryset(self):
        user = User.objects.filter(role='COSTUMER')
        return user
    

class AdminVendorListView(generics.ListAPIView):
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return User.objects.filter(role='VENDOR')
    

class AdminUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def perform_update(self, serializer):
        user = serializer.save()

        ActivityLog.objects.create(
            user=self.request.user,
            action='ROLE_CHANGE',
            description=f"Changed role of {user.username} to {user.role}"
        )
    
        
