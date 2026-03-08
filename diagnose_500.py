import os
import sys

# Mock dj_database_url since it's missing in the env
import types
mock_dj = types.ModuleType('dj_database_url')
mock_dj.config = lambda **kwargs: {}
sys.modules['dj_database_url'] = mock_dj

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

try:
    import django
    django.setup()
    
    from conversation.views import ConversationViewSet
    from conversation.serializers import ConversationSerializer
    from conversation.models import Conversation
    from accounts.models import User
    
    print("Imports successful!")
    
    # Try to initialize the viewset and serializer to check for common errors
    viewset = ConversationViewSet()
    print("ViewSet initialized!")
    
    serializer = ConversationSerializer()
    print("Serializer initialized!")
    
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
