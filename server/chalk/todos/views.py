"""
Views for todo app
"""
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from chalk.todos.models import LabelModel, TodoModel
from chalk.todos.serializers import LabelSerializer, TodoSerializer
from chalk.todos.oauth import get_authorization_url


@api_view(['GET'])
def auth(request):
    """
    API endpoint that redirects a user to Google for login
    """
    return redirect(get_authorization_url())


@api_view(['GET'])
def auth_callback(request):
    """
    API endpoint that handles the Google OAuth callback to log the user in
    """
    user = authenticate(request, token=request.GET['code'])
    if user is not None:
        login(request, user)
        return redirect('/')

    # Return an 'invalid login' error message.
    return Response('Not authenticated', status=401)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def auth_test(request):
    """
    API endpoint that checks if a user is logged in
    """
    return Response('Logged in!')


@api_view(['GET', 'HEAD'])
def healthz(request):
    """
    API endpoint that indicates the server is healthy
    """
    return Response('Healthy!')


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
