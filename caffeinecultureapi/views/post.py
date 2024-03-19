from django.http import HttpResponseServerError
from django.db.models import Count
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.decorators import action
from caffeinecultureapi.models import Post, User, Category, Like
from django.core.paginator import Paginator
from django.db.models import Count, Value, BooleanField
from .comment import CommentSerializer
from .helpers import get_user_by_uid

class PostView(ViewSet):
    """Level up post view"""
    
    def __get_posts_likes(self, posts, user):
        
        # Private method to update like_count on post model for post list requests
    
        for post in posts:
            likes = Like.objects.filter(post = post.pk)
            post.like_count += len(likes)
            
            liked = Like.objects.filter(post=post, user=user).exists()
            
            post.liked = liked
        
        return posts
    
    def __get_filtered_posts(self, user, query):
        
        posts = Post.objects.all()
        
        posts = self.__get_posts_likes(posts, user)
        
        if query == 'newest':
            return posts.order_by('-id')
        else:
            return posts.order_by('id')


    def retrieve(self, request, pk):
        """Handle GET requests for single posts

        Returns:
            Response -- JSON serialized post
        """
        
        # Retrieves UID passed through headers
        uid = request.META['HTTP_AUTHORIZATION']
        
        if not uid:
            return Response({"error": "Authorization header is missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_user_by_uid(uid)
        
        try:
            post = Post.objects.get(pk=pk)
            
            likes = Like.objects.filter(post = post.pk)
            post.like_count += len(likes)
            
            liked = Like.objects.filter(post=post, user=user).exists()
            
            post.liked = liked
                
            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist as ex:
            return Response({'Post does not exist': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        """Handle GET requests to get all posts

        Returns:
            Response -- JSON serialized list of posts
        """
        # Retrieves UID passed through headers
        uid = request.META['HTTP_AUTHORIZATION']
        
        if not uid:
            return Response({"error": "Authorization header is missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_user_by_uid(uid)
        
        posts = Post.objects.order_by('-id')
        
        posts = self.__get_posts_likes(posts, user)

        # paginator = Paginator(posts, per_page=2)
        
        # print(paginator.num_pages)
            
        serializer = PostSerializer(posts, many=True)
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
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['get'], detail=False)
    def get_user_posts(self, request):
        """Returns a single users posts 
        Returns:
            Response: Serialized data with 200 OK
        """
        
        # Retrieves UID passed through headers
        uid = request.META['HTTP_AUTHORIZATION']
        
        if not uid:
            return Response({"error": "Authorization header is missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_user_by_uid(uid)

        posts = Post.objects.filter(user=user).order_by('-id')

        posts = self.__get_posts_likes(posts, user)

            
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False)
    def get_paginated_posts(self, request):
        """Handle GET requests to get all paginated posts

        Returns:
            Response -- JSON serialized list of posts
        """
        # Retrieves UID passed through headers
        uid = request.META['HTTP_AUTHORIZATION']
        
        page = request.data["page"]
        
        if not uid:
            return Response({"error": "Authorization header is missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_user_by_uid(uid)

        posts = Post.objects.order_by('-id')
        
        posts = self.__get_posts_likes(posts, user)

        paginator = Paginator(posts, per_page=2)
        
        posts =  paginator.page(page)
            
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False)
    def get_filtered_posts(self, request):
        uid = request.META['HTTP_AUTHORIZATION']
        
        query =  request.GET.get('filter', None)
        
        if not uid:
            return Response({"error": "Authorization header is missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_user_by_uid(uid)

        posts = self.__get_filtered_posts(user, query)
        
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False)
    def search_posts(self, request):
        """Handle GET requests to get all paginated posts

        Returns:
            Response -- JSON serialized list of posts
        """
        # Retrieves UID passed through headers
        uid = request.META['HTTP_AUTHORIZATION']
        
        if not uid:
            return Response({"error": "Authorization header is missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        search =  request.GET.get('search', None)
        
        user = get_user_by_uid(uid)

        posts = Post.objects.filter(title__contains=search)
        
        posts = self.__get_posts_likes(posts, user)
        
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostSerializer(serializers.ModelSerializer):
    """JSON serializer for posts

    """
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'date', 'like_count', 'category', 'user', 'comments', 'liked')
        depth = 1
        