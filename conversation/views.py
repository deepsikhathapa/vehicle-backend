from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Conversation, Message, ReadReceipt
from .serializers import (
    ReadReceiptSerializer, MessageSerializer, ConversationCreateSerializer,
    ConversationSerializer
)
from django.db.models import Q, Max
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# Create your views here.

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Conversation.objects.none()
        return Conversation.objects.filter(
            Q(customer=user) | Q(vendor=user)
        ).select_related('customer', 'vendor').prefetch_related('messages')
    
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        # Return full conversation data using the read serializer
        read_serializer = ConversationSerializer(
            conversation,
            context={'request': request}
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        page_size = int(request.query_params.get('page_size', 50))
        page = int(request.query_params.get('page', 1))

        messages = conversation.messages.all()

        start = (page - 1) * page_size
        end = start + page_size
        paginated_messages = messages[start:end]
        
        serializer = MessageSerializer(
            paginated_messages, 
            many=True,
            context={'request': request}
        )

        return Response({
            'count': messages.count(),
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        conversation = self.get_object()
        
        messages = conversation.messages.exclude(sender=request.user)
        
        for message in messages:
            ReadReceipt.objects.get_or_create(
                message=message,
                user=request.user
            )
        
        return Response({'status': 'marked as read'})
    


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(conversation__customer=user) | Q(conversation__vendor=user)
        ).select_related('sender', 'conversation')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        conversation_id = self.request.data.get('conversation')
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if self.request.user not in [conversation.customer, conversation.vendor]:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer.save(sender=self.request.user)
        
        conversation.updated_at = timezone.now()
        conversation.save()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.sender != request.user:
            return Response(
                {'error': 'Not authorized to edit this message'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance.content = request.data.get('content', instance.content)
        instance.is_edited = True
        instance.edited_at = timezone.now()
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a specific message as read"""
        message = self.get_object()

        if message.sender == request.user:
            return Response(
                {'error': 'Cannot mark own message as read'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        read_receipt, created = ReadReceipt.objects.get_or_create(
            message=message,
            user=request.user
        )
        
        return Response({
            'status': 'marked as read',
            'created': created
        })

    

    
    

    
