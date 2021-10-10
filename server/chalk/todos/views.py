"""
Views for serving reinforcement learning details
"""

from rest_framework import permissions, viewsets

from chalk.todos.models import LabelModel, TodoModel
from chalk.todos.serializers import LabelSerializer, TodoSerializer


class TodoViewSet(viewsets.ModelViewSet):  # pylint: disable=R0901
    """
    API endpoint that allows viewing or editing a todo.
    """
    queryset = TodoModel.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [permissions.AllowAny]  # permissions.IsAuthenticated


class LabelViewSet(viewsets.ModelViewSet):  # pylint: disable=R0901
    """
    API endpoint that allows viewing or editing a label.
    """
    queryset = LabelModel.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [permissions.AllowAny]  # permissions.IsAuthenticated
