from django.urls import path
from .views import ActivityLogview

urlpatterns = [
    path('admin/', ActivityLogview.as_view()),
]