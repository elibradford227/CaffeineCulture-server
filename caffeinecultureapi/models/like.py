from django.db import models
from .user import User
from .post import Post

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post')