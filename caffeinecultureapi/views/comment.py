from django.http import HttpResponseServerError
from django.db.models import Count
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers, status
from .notification import NotificationView
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
            serialized = []
            if comment.parent is None:
                comment_family = comment.get_children()
                print(comment_family)
                serialized_family = CommentSerializer(comment_family, many=True).data
                serialized.extend(serialized_family)
            # serializer = CommentSerializer(comment, context={'request': request})
            print(serialized)
            return Response(serialized, status=status.HTTP_200_OK)
        except Comment.DoesNotExist as ex:
            return Response({'comment does not exist': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        """Handle GET requests to get all comments

        Returns:
            Response -- JSON serialized list of comments
        """
        comments = Comment.objects.all()
        serialized = []
        
        for comment in comments:
            if comment.parent is None:
                comment_family = comment.get_children()
                serialized_family = CommentSerializer(comment_family, many=True).data
                serialized.extend(serialized_family)
        
        return Response(serialized, status=status.HTTP_200_OK)
      
    def create(self, request):
        """Handle comment operations

        Returns
          Response -- JSON serialized comment instance
        """
        
        user=User.objects.get(uid=request.data["uid"])
        post=Post.objects.get(pk=request.data["post"])
         
        poster = User.objects.get(id=post.user_id)
        
        comment = Comment.objects.create(
            user = user,
            post = post,
            content = request.data["content"]
        )
        
        if (user != poster):
            NotificationView().create_post_notification(post, user, poster)
        
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
    
    @action(methods=['post'], detail=True)
    def create_reply(self, request, pk):
        """Creates a reply comment
        Returns:
            Response: Success message with 204 code
        """
        try:
            parent_comment = Comment.objects.get(pk=pk)
            
            parent = User.objects.get(id=parent_comment.user.id)
            
            user=User.objects.get(uid=request.data["uid"])
            post=Post.objects.get(pk=request.data["post"])
        
            comment = Comment.objects.create(
                user = user,
                post = post,
                content = request.data["content"],
                parent = parent_comment
            )
            
            if (user != parent):
                NotificationView().create_reply_notification(parent_comment, user, parent)

            serializer = CommentSerializer(comment, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response('User not found', status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response('Post not found', status=status.HTTP_404_NOT_FOUND)
    
    @action(methods=['get'], detail=True)
    def get_single_post_comments(self, request, pk):
        """Returns a single posts comments with nested replies
        Returns:
            Response: Success message with 204 code
        """
        
        post = Post.objects.get(pk=pk)
        comments = Comment.objects.filter(post=post).order_by('-id')
        
        serialized = []
        
        for comment in comments:
            if comment.parent is None:
                comment_family = comment.get_children()
                serialized_family = CommentSerializer(comment_family, many=True).data
                serialized.extend(serialized_family)
        
        return Response(serialized, status=status.HTTP_200_OK)
        

        

class CommentSerializer(serializers.ModelSerializer):
    """JSON serializer for comments

    """
    class Meta:
        model = Comment
        fields = ('id', 'user', 'post', 'content', 'date', 'parent')
        depth = 2
        

        