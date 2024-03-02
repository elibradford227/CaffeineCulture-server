from django.http import HttpResponseServerError
from django.db.models import Count, F, Q
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers, status
from caffeinecultureapi.models import Post, User, Message

class MessageView(ViewSet):
    """Level up message view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single messages

        Returns:
            Response -- JSON serialized message
        """
        try:
            message = Message.objects.get(pk=pk)
            serializer = MessageSerializer(message, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Message.DoesNotExist as ex:
            return Response({'message does not exist': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        """Handle GET requests to get all messages

        Returns:
            Response -- JSON serialized list of messages
        """
        message = Message.objects.all()
        serializer = MessageSerializer(message, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
    def create(self, request):
        """Handle message operations

        Returns
          Response -- JSON serialized message instance
        """
        
        sender=User.objects.get(uid=request.data["sender_uid"])
        receiver=User.objects.get(uid=request.data["receiver_uid"])
        

        message = Message.objects.create(
            sender = sender,
            receiver = receiver,
            content = request.data["content"]
        )

        serializer = MessageSerializer(message, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk):
        """Handle PUT requests for a message

        Returns:
          Response -- Empty body with 204 status code
        """

        message = Message.objects.get(pk=pk)
        
        sender=User.objects.get(uid=request.data["sender_uid"])
        message.sender=sender
        
        receiver=User.objects.get(uid=request.data["receiver_uid"])
        message.receiver=receiver
        
        message.content = request.data["content"]
        

        message.save()
        
        serializer = MessageSerializer(message, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, response, pk):
        """Deletes Data

        Returns:
            Response: Empty body with 204 code
        """
        message = Message.objects.get(pk=pk)
        message.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False)
    def get_conversation(self, request):
        """Returns conversation history between two users
            Returns:
                Response: Serialized data with 200 OK
            """
            
        sender=User.objects.get(uid=request.data["sender_uid"])
        receiver=User.objects.get(uid=request.data["receiver_uid"])
        
        messages = Message.objects.filter(Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)).order_by('date')
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageSerializer(serializers.ModelSerializer):
    """JSON serializer for messages

    """
    class Meta:
        model = Message
        fields = ('id', 'sender', 'receiver', 'content', 'date')
        depth = 1

        