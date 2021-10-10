"""
Django Rest Framework serializers for todos
"""
from rest_framework import serializers

from chalk.todos.models import LabelModel, TodoModel


class TodoSerializer(serializers.ModelSerializer):
    """
    Serializer for todos
    """

    class Meta:
        model = TodoModel
        fields = [
            'archived',
            'archived_at',
            'completed',
            'completed_at',
            'created_at',
            'description',
            'id',
        ]


class LabelSerializer(serializers.ModelSerializer):
    """
    Serializer for labels
    """

    class Meta:
        model = LabelModel
        fields = [
            'id',
            'name',
        ]
