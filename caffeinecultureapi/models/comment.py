from django.db import models
from .user import User
from .post import Post

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, related_name='children')
    
    def get_children(self):
        children = list()
        children.append(self)
        for child in self.children.all():
            children.extend(child.get_children())
        return children