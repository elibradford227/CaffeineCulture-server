from django.http import HttpResponseServerError
from django.db.models import Count
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from caffeinecultureapi.models import Category

class CategoryView(ViewSet):
    """Level up category view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single categories

        Returns:
            Response -- JSON serialized category
        """
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist as ex:
            return Response({'category does not exist': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        """Handle GET requests to get all categories

        Returns:
            Response -- JSON serialized list of categories
        """
        category = Category.objects.all()
        serializer = CategorySerializer(category, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CategorySerializer(serializers.ModelSerializer):
    """JSON serializer for categories

    """
    class Meta:
        model = Category
        fields = ('id', 'name')

        