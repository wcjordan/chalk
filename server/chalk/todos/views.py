"""
Views for todo app
"""
from datetime import datetime, timezone
import json
import math
import random
import statistics

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from google.cloud import storage
from rest_framework import permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from chalk.todos.consts import RANK_ORDER_DEFAULT_STEP
from chalk.todos.models import LabelModel, RankOrderMetadata, TodoModel
from chalk.todos.serializers import LabelSerializer, TodoSerializer
from chalk.todos.oauth import get_authorization_url
from chalk.todos.signals import rebalance_rank_order

SESSION_BUCKET_ID = 'flipperkid-chalk-web-session-data'


@api_view(['GET'])
def auth(request):
    """
    API endpoint that redirects a user to Google for login
    """
    return redirect(get_authorization_url(request.get_host()))


@api_view(['GET'])
def auth_callback(request):
    """
    API endpoint that handles the Google OAuth callback to log the user in
    """
    user = authenticate(request, token=request.GET['code'])
    if user is not None:
        login(request, user)

        if 'state' in request.GET or 'ci_refresh' in request.GET:
            return redirect('/')
        return Response('Logged in!')

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


@api_view(['POST', 'HEAD'])
@permission_classes([permissions.IsAuthenticated])
def log_session_data(request):
    """
    API endpoint used to log session data to an object storage bucket
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(SESSION_BUCKET_ID)
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d_%H:%M:%S.%f%z')
    filename = f"{timestamp}_{random.randint(0, 9999):04}"
    blob = bucket.blob(filename)
    blob.upload_from_string(json.dumps(request.data))

    return Response('Session data logged!')


@api_view(['GET', 'HEAD'])
@permission_classes([permissions.IsAdminUser])
def status(request):
    """
    API endpoint that returns status info about the server
    """
    metadata = RankOrderMetadata.objects.first()
    todos = TodoModel.objects.filter(archived=False)
    return Response({
        'closest_rank_min': metadata.closest_rank_min,
        'closest_rank_max': metadata.closest_rank_max,
        'closest_rank_distance': metadata.closest_rank_distance,
        'closest_rank_steps': metadata.closest_rank_steps,
        'last_rebalanced_at': metadata.last_rebalanced_at,
        'last_rebalance_duration': metadata.last_rebalance_duration,
        'max_rank': metadata.max_rank,
        'todos_count': todos.count(),
        'incomplete_todos_count': todos.filter(completed=False).count(),
    })


@api_view(['POST', 'HEAD'])
@permission_classes([permissions.IsAdminUser])
def rebalance_ranks(request):
    """
    API endpoint that manually triggers an order rank rebalance
    """
    rebalance_rank_order()
    return Response('Rebalanced!')


class TodoViewSet(viewsets.ModelViewSet):  # pylint: disable=R0901
    """
    API endpoint that allows viewing or editing a todo.
    """
    queryset = TodoModel.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    # pylint: disable=unused-argument,invalid-name
    def reorder(self, request, pk=None):
        """
        Reorder a todo to be in the middle of 2 todos specified by their IDs.

        """
        relative_id = request.data.get('relative_id')
        position = request.data.get('position')
        if not relative_id:
            return Response(
                "A 'relative_id' must be provided representing the "
                "todo to order this todo relative to",
                status=400)
        if position not in ['before', 'after']:
            return Response(
                "A 'position' must be provided ('before' or 'after')",
                status=400)

        relative_order_rank = TodoModel.objects.get(id=relative_id).order_rank
        if position == 'before':
            next_order_rank = relative_order_rank
            prev_todo = TodoModel.objects.all().filter(
                order_rank__lt=relative_order_rank).order_by(
                    '-order_rank').first()

            prev_order_rank = 0
            if prev_todo is not None:
                prev_order_rank = prev_todo.order_rank
        else:
            prev_order_rank = relative_order_rank
            next_todo = TodoModel.objects.all().filter(
                order_rank__gt=relative_order_rank).order_by(
                    'order_rank').first()

            next_order_rank = prev_order_rank + (2 * RANK_ORDER_DEFAULT_STEP)
            if next_todo is not None:
                next_order_rank = next_todo.order_rank

        todo = self.get_object()
        todo.order_rank = math.floor(
            statistics.mean([prev_order_rank, next_order_rank]))
        todo.save()

        order_metadata = RankOrderMetadata.objects.first()
        distance = todo.order_rank - prev_order_rank
        if distance < order_metadata.closest_rank_distance:
            order_metadata.closest_rank_min = prev_order_rank
            order_metadata.closest_rank_max = todo.order_rank
            order_metadata.save()

        serializer = self.get_serializer(todo)
        return Response(serializer.data)


class LabelViewSet(viewsets.ModelViewSet):  # pylint: disable=R0901
    """
    API endpoint that allows viewing or editing a label.
    """
    queryset = LabelModel.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated]
