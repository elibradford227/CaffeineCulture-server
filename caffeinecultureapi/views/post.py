from django.http import HttpResponseServerError
from django.db.models import Count
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from caffeinecultureapi.models import Post, User, Category

class PostView(ViewSet):
    """Level up post view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single posts

        Returns:
            Response -- JSON serialized post
        """
        try:
            post = Post.objects.get(pk=pk)
            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist as ex:
            return Response({'Post does not exist': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        """Handle GET requests to get all posts

        Returns:
            Response -- JSON serialized list of posts
        """
        post = Post.objects.all()
        serializer = PostSerializer(post, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
    def create(self, request):
        """Handle POST operations

        Returns
          Response -- JSON serialized post instance
        """
        
        user=User.objects.get(uid=request.data["uid"])
        category=Category.objects.get(pk=request.data["category"])
        
        post = Post.objects.create(
            title = request.data["title"],
            content = request.data["content"],
            user = user,
            category = category
        )

        serializer = PostSerializer(post, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk):
        """Handle PUT requests for a post

        Returns:
          Response -- Empty body with 204 status code
        """

        post = Post.objects.get(pk=pk)
      
        post.title = request.data["title"]
        post.content = request.data["content"]
        
        user=User.objects.get(uid=request.data["uid"])
        post.user=user
        
        category=Category.objects.get(pk=request.data["category"])
        post.category=category

        post.save()
        
        serializer = PostSerializer(post, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, response, pk):
        """Deletes Data

        Returns:
            Response: Empty body with 204 code
        """
        post = Post.objects.get(pk=pk)
        post.delete()
        return response(None, status=status.HTTP_204_NO_CONTENT)
        

class PostSerializer(serializers.ModelSerializer):
    """JSON serializer for posts

    """
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'date', 'like_count', 'category', 'user')
        depth = 1
        