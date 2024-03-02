from django.db import models
from .user import User

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')