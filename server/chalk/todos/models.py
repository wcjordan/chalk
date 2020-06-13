"""
Django ORM models for Todos
"""
from django.db import models


class TodoModel(models.Model):
    """
    A todo
    """
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description
