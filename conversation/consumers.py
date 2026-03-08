import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Conversation, Message, ReadReceipt, TypingIndicator, User


class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        has_access = await self.check_conversation_access()
        if not has_access:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        await self.set_user_online(True)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_online': True
            }
        )
    
    async def disconnect(self, close_code):

        await self.update_typing_status(False)
        
        await self.set_user_online(False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_online': False
            }
        )
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read_receipt':
                await self.handle_read_receipt(data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def handle_chat_message(self, data):
        content = data.get('content', '')

        try:
            message = await self.save_message(content)
        except Exception as e:
            import traceback
            traceback.print_exc()
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to save message: {str(e)}'
            }))
            return
        
        if message:
            # Safely get avatar - User model may not have an avatar field
            avatar = None
            sender_avatar = getattr(message.sender, 'avatar', None)
            if sender_avatar:
                try:
                    avatar = sender_avatar.url
                except (ValueError, AttributeError):
                    avatar = None

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'sender': {
                            'id': message.sender.id,
                            'username': message.sender.username,
                            'avatar': avatar
                        },
                        'created_at': message.created_at.isoformat(),
                        'is_edited': message.is_edited
                    }
                }
            )
    
    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)

        await self.update_typing_status(is_typing)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing
            }
        )
    
    async def handle_read_receipt(self, data):

        message_id = data.get('message_id')
        
        if message_id:
            receipt_created = await self.create_read_receipt(message_id)
            
            if receipt_created:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'read_receipt',
                        'message_id': message_id,
                        'user_id': self.user.id,
                        'username': self.user.username
                    }
                )
    
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def typing_indicator(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))
    
    async def user_status(self, event):
        """Send user online/offline status to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_online': event['is_online']
        }))
    
    async def read_receipt(self, event):
        """Send read receipt to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    @database_sync_to_async
    def check_conversation_access(self):
        """Check if user has access to conversation"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return self.user in [conversation.customer, conversation.vendor]
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            
            # Check if user is actually part of the conversation
            if self.user not in [conversation.customer, conversation.vendor]:
                 return None

            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content
            )
            conversation.updated_at = timezone.now()
            conversation.save()
            return message
        except Conversation.objects.model.DoesNotExist:
            return None
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None
    
    @database_sync_to_async
    def update_typing_status(self, is_typing):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            indicator, created = TypingIndicator.objects.get_or_create(
                conversation=conversation,
                user=self.user
            )
            indicator.is_typing = is_typing
            indicator.save()
        except Conversation.DoesNotExist:
            pass
    
    @database_sync_to_async
    def create_read_receipt(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            if message.sender == self.user:
                return False
            
            ReadReceipt.objects.get_or_create(
                message=message,
                user=self.user
            )
            return True
        except Message.DoesNotExist:
            return False
    
    @database_sync_to_async
    def set_user_online(self, is_online):
        self.user.is_online = is_online
        if not is_online:
            self.user.last_seen = timezone.now()
        self.user.save()