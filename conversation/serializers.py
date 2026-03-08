from rest_framework import serializers
from .models import Conversation, Message, ReadReceipt, TypingIndicator
from accounts.serializers import UserSerializer
from accounts.models import User


class ReadReceiptSerializer(serializers.ModelSerializer):
    user  = UserSerializer(read_only=True)

    class Meta:
        model = ReadReceipt
        fields = ['id', 'user', 'message', 'read_at']
        read_only_fields = ['id', 'read_at']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    read_receipts = ReadReceiptSerializer(many=True, read_only=True)
    is_read = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'sender',
            'content',
            'file',
            'file_url',
            'created_at',
            'edited_at',
            'is_edited',
            'is_read',
            'read_receipts'
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'edited_at', 'is_edited']

    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.read_receipts.filter(user=request.user).exists()
        return False

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class ConversationSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    vendor = UserSerializer(read_only=True)
    last_message = MessageSerializer(read_only=True, allow_null=True)
    unread_count = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'customer', 'vendor', 'created_at', 'updated_at',
                  'last_message', 'unread_count', 'other_user']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            messages = obj.messages.exclude(sender=request.user)
            unread = messages.exclude(
                read_receipts__user=request.user
            ).count()
            return unread
        return 0

    def get_other_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_user = obj.vendor if request.user == obj.customer else obj.customer
            if other_user:
                return UserSerializer(other_user, context=self.context).data
        return None


class ConversationCreateSerializer(serializers.ModelSerializer):
    other_user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Conversation
        fields = ['other_user_id']

    def validate_other_user_id(self, value):
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        request_user = self.context['request'].user
        if user.role == request_user.role:
            raise serializers.ValidationError(
                "Can only create conversations between customers and vendors"
            )
        return value
    
    def create(self, validated_data):
        other_user_id = validated_data.pop('other_user_id')
        other_user = User.objects.get(id=other_user_id)
        request_user = self.context['request'].user

        if request_user.role == 'CUSTOMER':
            customer = request_user
            vendor = other_user
        else:
            customer = other_user
            vendor = request_user

        conversation, created = Conversation.objects.get_or_create(
            customer=customer,
            vendor=vendor
        )
        return conversation


    

