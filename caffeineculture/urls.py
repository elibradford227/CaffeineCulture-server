"""caffeineculture URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from caffeinecultureapi.views import check_user, register_user, PostView, CommentView, CategoryView, LikeView, get_user_by_name, MessageView, ConversationView, NotificationView, get_user_by_id

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'posts', PostView, 'posts')
router.register(r'comments', CommentView, 'comments')
router.register(r'categories', CategoryView, 'categories')
router.register(r'likes', LikeView, 'likes')
router.register(r'messages', MessageView, 'messages')
router.register(r'conversations', ConversationView, 'conversations')
router.register(r'notifications', NotificationView, 'notifications')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('register', register_user),
    path('checkuser', check_user),
    path('get_user_by_name', get_user_by_name),
    path('get_user_by_id', get_user_by_id),
]
