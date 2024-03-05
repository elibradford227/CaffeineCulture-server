from django.db import models
from .user import User
from .post import Post
from .comment import Comment
from .message import Message

class Notification(models.Model):
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='poster', null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='commenter', null=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='messager', null=True)