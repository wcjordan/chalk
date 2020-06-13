"""
Views for serving reinforcement learning details
"""

from rest_framework import permissions, viewsets

from chalk.todos.models import TodoModel
from chalk.todos.serializers import TodoSerializer


class TodoViewSet(viewsets.ModelViewSet):  # pylint: disable=R0901
    """
    API endpoint that allows viewing or editing a todo.
    """
    queryset = TodoModel.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [permissions.AllowAny]  # permissions.IsAuthenticated
