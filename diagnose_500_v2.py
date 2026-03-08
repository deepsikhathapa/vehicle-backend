import os
import sys
import types

# Robust mocking for missing dependencies
def mock_module(name, **kwargs):
    m = types.ModuleType(name)
    for k, v in kwargs.items():
        setattr(m, k, v)
    sys.modules[name] = m
    return m

mock_dj = mock_module('dj_database_url', config=lambda **kwargs: {})
mock_dec = mock_module('decouple', 
    config=lambda key, default=None: default,
    Config=types.MethodType(lambda self, repo: None, object),
    RepositoryEnv=lambda x: None,
    Csv=lambda: None
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

try:
    import django
    django.setup()
    
    from conversation.views import ConversationViewSet
    from conversation.serializers import ConversationSerializer
    from conversation.models import Conversation
    from accounts.models import User
    from rest_framework.test import APIRequestFactory
    from rest_framework import permissions
    
    print("Imports successful!")
    
    # Create a mock user
    user = User.objects.first()
    if not user:
        print("No users in DB, creating mock user...")
        user = User.objects.create(username='test_diagnostic_user', role='COSTUMER')
    
    factory = APIRequestFactory()
    request = factory.get('/api/conversation/conversations/')
    request.user = user
    
    view = ConversationViewSet.as_view({'get': 'list'})
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 500:
        print("Response data (if any):", response.data)
    else:
        print("Request successful (code 200/other)!")
        
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
