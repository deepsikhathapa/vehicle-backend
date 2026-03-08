from django.db import models
from accounts.models import User

# Create your models here.

class Conversation(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversation_customer',
        limit_choices_to={'role': 'CUSTOMER'}
    )
    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversation_vendor',
        limit_choices_to={'role': 'VENDOR'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['customer', 'vendor']
        ordering = ['-updated_at']

    def __str__(self):
        return f'conversation: {self.customer.username} - {self.vendor.username}'
    
    @property
    def last_message(self):
        return self.messages.first()
    

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    file = models.FileField(
        upload_to='chat_files/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)


    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"
    

class ReadReceipt(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_receipts'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    read_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ['message', 'user']

    def __str__(self):
        return f'{self.user.username} read message {self.message.id}'
    

class TypingIndicator(models.Model):
    conversation =  models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='typing_indicators'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    is_typing = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ['conversation', 'user']

    def __str__(self):
        return f'{self.user.username} typing in {self.conversation.id}'

