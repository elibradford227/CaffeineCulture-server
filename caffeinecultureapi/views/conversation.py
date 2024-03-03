from django.http import HttpResponseServerError
from django.db.models import Count
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers, status
from caffeinecultureapi.models import Post, User, Conversation

class ConversationView(ViewSet):
    """Level up conversation view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single conversations

        Returns:
            Response -- JSON serialized conversation
        """
        try:
            conversation = Conversation.objects.get(pk=pk)
            serializer = ConversationSerializer(conversation, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Conversation.DoesNotExist as ex:
            return Response({'conversation does not exist': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        """Handle GET requests to get all conversations

        Returns:
            Response -- JSON serialized list of conversations
        """
        conversations = Conversation.objects.all()
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
    def create(self, request):
        """Handle conversation operations

        Returns
           Response -- JSON serialized conversation instance
        """
        
        user_one=User.objects.get(uid=request.data["one_uid"])
        user_two=User.objects.get(uid=request.data["two_uid"])
        
        exists = Conversation.objects.filter(participants=user_one).filter(participants=user_two).exists()
        
        if exists: 
            return Response({"error": "Conversation already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        conversation = Conversation.objects.create()
        
        conversation.participants.add(user_one)
        conversation.participants.add(user_two)

        serializer = ConversationSerializer(conversation, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, response, pk):
        """Deletes Data

        Returns:
            Response: Empty body with 204 code
        """
        conversation = Conversation.objects.get(pk=pk)
        conversation.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['get'], detail='True')
    def get_users_conversations(self, request, pk):
        """Returns a list of all users conversations
        Returns:
            Response: Success message with 200 code
        """
        user = User.objects.get(pk=pk)
        
        conversations = Conversation.objects.filter(participants=user).order_by('-id')
        
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'uid')
      
class ConversationSerializer(serializers.ModelSerializer):
    """JSON serializer for conversations

    """
    participants = UserSerializer(many=True)
    
    class Meta:
        model = Conversation
        fields = ('id', 'participants')
        depth = 1