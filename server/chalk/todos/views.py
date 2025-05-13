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
from django.core.exceptions import ValidationError
from google.cloud import storage
from rest_framework import permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from chalk.todos.consts import RANK_ORDER_DEFAULT_STEP
from chalk.todos.models import LabelModel, RankOrderMetadata, TodoModel
from chalk.todos.serializers import LabelSerializer, TodoSerializer
from chalk.todos.oauth import get_authorization_url
from chalk.todos.signals import rebalance_rank_order
from chalk.todos.views import _validate_session_data, MAX_SESSION_DATA_SIZE, MAX_SESSION_KEYS

SESSION_BUCKET_ID = 'flipperkid-chalk-web-session-data'
MAX_SESSION_DATA_SIZE = 1024 * 1024  # 1 MiB limit
MAX_SESSION_KEYS = 3  # Maximum number of keys in the session data


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

    Validates and sanitizes data before storing:
    - Enforces size limits (1 MiB max)
    - Limits number of keys
    - Validates data structure
    """
    try:
        data_str = json.dumps(request.data)

        # Validate the session data
        _validate_session_data(request.data, data_str)

        # Sanitize data by re-encoding through JSON
        sanitized_data = json.loads(data_str)

        # Store the sanitized data
        storage_client = storage.Client()
        bucket = storage_client.bucket(SESSION_BUCKET_ID)
        timestamp = datetime.now(
            timezone.utc).strftime('%Y-%m-%d_%H:%M:%S.%f%z')
        filename = f"{timestamp}_{random.randint(0, 9999):04}"
        blob = bucket.blob(filename)
        blob.upload_from_string(json.dumps(sanitized_data))

        return Response('Session data logged!')
    except ValidationError as e:
        return Response({'error': str(e)}, status=400)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid JSON data format'}, status=400)


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


def _validate_session_data(data, data_str):
    """
    Validates session data to ensure it meets security requirements

    Args:
        data: The session data to validate
        data_str: The string representation of the session data

    Raises:
        ValidationError: If the data fails validation
    """
    # Check overall data size
    if len(data_str) > MAX_SESSION_DATA_SIZE:
        raise ValidationError(
            (f"Session data exceeds maximum size of {MAX_SESSION_DATA_SIZE} "
             "bytes"))

    # Check the structure of the session data
    if not isinstance(data, dict):
        raise ValidationError("Session data must be a dictionary")
    if 'environment' not in data:
        raise ValidationError("Session data must contain an 'environment' key")
    if 'session_guid' not in data:
        raise ValidationError("Session data must contain a 'session_guid' key")
    if 'session_data' not in data:
        raise ValidationError("Session data must contain a 'session_data' key")

    # Check number of keys to prevent DoS attacks
    if isinstance(data, dict) and len(data) > MAX_SESSION_KEYS:
        raise ValidationError(
            f"Session data contains too many keys (max: {MAX_SESSION_KEYS})")
