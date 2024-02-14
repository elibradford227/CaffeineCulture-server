from django.db import models

class User(models.Model):
    username = models.CharField(max_length=20)
    bio = models.CharField(max_length=250)
    join_date = models.DateTimeField(auto_now_add=True)
    uid = models.CharField(max_length = 50)