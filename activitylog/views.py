from django.shortcuts import render
from rest_framework import permissions, generics
from .models import ActivityLog
from .serializers import ActivityLogSerializer
from accounts.permissions import IsAdmin

# Create your views here.

class ActivityLogview(generics.ListAPIView):
    queryset = ActivityLog.objects.all().order_by('-created_at')
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
