"""
Django Rest Framework serializers for todos
"""
from rest_framework import serializers

from chalk.todos.models import TodoModel


class TodoSerializer(serializers.ModelSerializer):
    """
    Serializer for todos
    """

    class Meta:
        model = TodoModel
        fields = ['id', 'description', 'created_at']
