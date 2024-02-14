from django.db import models
from .user import User
from .category import Category

class Post(models.Model):
    title = models.CharField(max_length=20)
    content = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
    like_count = 0
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)