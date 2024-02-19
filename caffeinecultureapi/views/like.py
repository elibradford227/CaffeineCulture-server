from django.http import HttpResponseServerError
from django.db.models import Count, F
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers, status
from caffeinecultureapi.models import Post, User, Like

class LikeView(ViewSet):
    """Level up like view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single likes

        Returns:
            Response -- JSON serialized like
        """
        try:
            like = Like.objects.get(pk=pk)
            serializer = LikeSerializer(like, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Like.DoesNotExist as ex:
            return Response({'like does not exist': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        """Handle GET requests to get all likes

        Returns:
            Response -- JSON serialized list of likes
        """
        like = Like.objects.all()
        serializer = LikeSerializer(like, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
    def create(self, request):
        """Handle like operations

        Returns
          Response -- JSON serialized like instance
        """
        
        user=User.objects.get(uid=request.data["uid"])
        post=Post.objects.get(pk=request.data["post"])
        
        if Like.objects.filter(user=user, post=post):
            return Response('User has already liked post', status=status.HTTP_403_FORBIDDEN)
        else:
            like = Like.objects.create(
                user = user,
                post = post,
            )

        serializer = LikeSerializer(like, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk):
        """Handle PUT requests for a like

        Returns:
          Response -- Empty body with 204 status code
        """

        like = Like.objects.get(pk=pk)
        
        user=User.objects.get(uid=request.data["uid"])
        like.user=user
        
        post=Post.objects.get(pk=request.data["post"])
        like.post=post
        

        like.save()
        
        serializer = LikeSerializer(like, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, response, pk):
        """Deletes Data

        Returns:
            Response: Empty body with 204 code
        """
        like = Like.objects.get(pk=pk)
        like.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['get', 'delete'], detail=False)
    def delete_like(self, request, pk=None):
        """Deletes Like. Designed for deleting from front end
        Returns:
            Response: Success message with 204 code
        """
        try:
            user=User.objects.get(uid=request.data["uid"])
            post=Post.objects.get(pk=request.data["post"])
        
            like = Like.objects.get(user=user, post=post)
            like.delete()
            return Response('Like successfully deleted', status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response('User not found', status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response('Post not found', status=status.HTTP_404_NOT_FOUND)
        except Like.DoesNotExist:
            return Response('Like not found', status=status.HTTP_404_NOT_FOUND)
        

class LikeSerializer(serializers.ModelSerializer):
    """JSON serializer for likes

    """
    class Meta:
        model = Like
        fields = ('id', 'user', 'post')

        