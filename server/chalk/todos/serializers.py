"""
Django Rest Framework serializers for todos
"""
from rest_framework import serializers

from chalk.todos.models import LabelModel, TodoModel


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


class LabelStringField(serializers.StringRelatedField):
    """
    Serializer for labels based on their name field
    """

    def to_internal_value(self, data):
        return LabelModel.objects.get(name=data)


class TodoSerializer(serializers.ModelSerializer):
    """
    Serializer for todos
    """
    labels = LabelStringField(many=True)
    order_rank = serializers.IntegerField(read_only=True)

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
            'labels',
            'order_rank',
        ]
