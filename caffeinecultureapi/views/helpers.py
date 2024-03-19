from rest_framework.response import Response
from rest_framework import status
from caffeinecultureapi.models import User

def get_user_by_uid(uid):
    try:
        user = User.objects.get(uid=uid)
        return user
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)