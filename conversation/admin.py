from django.contrib import admin
from .models import Conversation, Message, ReadReceipt, TypingIndicator

# Register your models here.

admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(ReadReceipt)
admin.site.register(TypingIndicator)