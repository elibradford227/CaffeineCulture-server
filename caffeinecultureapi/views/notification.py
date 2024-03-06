from django.http import HttpResponseServerError
from django.db.models import Count, F, Q
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers, status
from caffeinecultureapi.models import Post, User, notification, Notification

class NotificationView(ViewSet):
    """Level up notification view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single notifications

        Returns:
            Response -- JSON serialized notification
        """
        try:
            notification = Notification.objects.get(pk=pk)
            serializer = NotificationSerializer(notification, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Notification.DoesNotExist as ex:
            return Response({'notification does not exist': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        """Handle GET requests to get all notifications

        Returns:
            Response -- JSON serialized list of notifications
        """
        notification = Notification.objects.all()
        serializer = NotificationSerializer(notification, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
    def create(self, request, id, type):
        """Handle notification operations

        Returns
          Response -- JSON serialized notification instance
        """
        
        sender=User.objects.get(uid=request.data["sender_uid"])
        receiver=User.objects.get(uid=request.data["receiver_uid"])
        

        notification = Notification.objects.create(
            is_read = False,
            sender = sender,
            receiver = receiver,
            content = request.data["content"]
        )

        serializer = NotificationSerializer(notification, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk):
        """Handle PUT requests for a notification

        Returns:
          Response -- Empty body with 204 status code
        """

        notification = Notification.objects.get(pk=pk)
        
        sender=User.objects.get(uid=request.data["sender_uid"])
        notification.sender=sender
        
        receiver=User.objects.get(uid=request.data["receiver_uid"])
        notification.receiver=receiver
        
        notification.content = request.data["content"]
        

        notification.save()
        
        serializer = NotificationSerializer(notification, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, response, pk):
        """Deletes Data

        Returns:
            Response: Empty body with 204 code
        """
        notification = Notification.objects.get(pk=pk)
        notification.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['get'], detail=False)
    def get_users_notifications(self, request):
        """
        Returns:
            Response: Success message with 200 code
        """
        # Retrieves UID passed through headers
        uid = request.META['HTTP_AUTHORIZATION']
        
        if not uid:
            return Response({"error": "Authorization header is missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(uid=uid)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
        notifications = Notification.objects.filter(user=user).order_by("-date")

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['get', 'patch'], detail=True)
    def mark_notification_read(self, request, pk):
        """
        Returns:
            Response: Success message with 200 code
        """

        try:
            notification = Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
        
        notification.is_read = True
        
        notification.save()
        
        serializer = NotificationSerializer(notification, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # TODO: Modularize three creates to reduce repetition 

    @action(methods=['post'], detail=False)
    def create_message_notification(self, message, receiver, sender):
        """
        Returns:
            Response: Success message with 204 code
        """
        
        username = receiver.username
    
        notification = Notification.objects.create(
            is_read = False,
            user = sender,
            message = message,
            content = username + ' sent you a message!'
        )

        serializer = NotificationSerializer(notification, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
    @action(methods=['post'], detail=False)
    def create_post_notification(self, post, commenter, poster):
        """
        Returns:
            Response: Success message with 204 code
        """
        
        username = commenter.username
    
        notification = Notification.objects.create(
            is_read = False,
            user = poster,
            post = post,
            content = username + ' commented on your post!'
        )

        serializer = NotificationSerializer(notification, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
    @action(methods=['post'], detail=False)
    def create_reply_notification(self, comment, commenter, parent):
        """
        Returns:
            Response: Success message with 204 code
        """
        
        username = commenter.username
    
        notification = Notification.objects.create(
            is_read = False,
            user = parent,
            comment = comment,
            content = username + ' replied to your comment!'
        )

        serializer = NotificationSerializer(notification, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NotificationSerializer(serializers.ModelSerializer):
    """JSON serializer for notifications

    """
    class Meta:
        model = Notification
        fields = ('id', 'is_read', 'user', 'message', 'post', 'comment', 'content', 'date')
        depth = 1

        