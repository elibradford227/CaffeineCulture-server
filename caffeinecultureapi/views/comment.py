from django.http import HttpResponseServerError
from django.db.models import Count
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from caffeinecultureapi.models import Post, User, Category, Comment

class CommentView(ViewSet):
    """Level up comment view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single comments

        Returns:
            Response -- JSON serialized comment
        """
        try:
            comment = Comment.objects.get(pk=pk)
            serializer = CommentSerializer(comment, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Comment.DoesNotExist as ex:
            return Response({'comment does not exist': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        """Handle GET requests to get all comments

        Returns:
            Response -- JSON serialized list of comments
        """
        comment = Comment.objects.all()
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
    def create(self, request):
        """Handle comment operations

        Returns
          Response -- JSON serialized comment instance
        """
        
        user=User.objects.get(uid=request.data["uid"])
        post=Post.objects.get(pk=request.data["post"])
        
        comment = Comment.objects.create(
            user = user,
            post = post,
            content = request.data["content"]
        )

        serializer = CommentSerializer(comment, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk):
        """Handle PUT requests for a comment

        Returns:
          Response -- Empty body with 204 status code
        """

        comment = Comment.objects.get(pk=pk)
        
        user=User.objects.get(uid=request.data["uid"])
        comment.user=user
        
        post=Post.objects.get(pk=request.data["post"])
        comment.post=post
        
        comment.content = request.data["content"]

        comment.save()
        
        serializer = CommentSerializer(comment, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, response, pk):
        """Deletes Data

        Returns:
            Response: Empty body with 204 code
        """
        comment = Comment.objects.get(pk=pk)
        comment.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
        

class CommentSerializer(serializers.ModelSerializer):
    """JSON serializer for comments

    """
    class Meta:
        model = Comment
        fields = ('id', 'user', 'post', 'content', 'date')
        depth = 1

        