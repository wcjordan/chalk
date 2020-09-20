"""
Django ORM models for Todos
"""
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


class TodoModel(models.Model):
    """
    A todo
    """
    archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return self.description


@receiver(pre_save, sender=TodoModel)
# pylint: disable=unused-argument
def update_timestamps(sender, instance, *args, **kwargs):
    """
    Before saving, update timestamps if necessary
    """
    if instance.completed and instance.completed_at is None:
        instance.completed_at = timezone.now()
    if not instance.completed and instance.completed_at is not None:
        instance.completed_at = None
    if instance.archived and instance.archived_at is None:
        instance.archived_at = timezone.now()
    if not instance.archived and instance.archived_at is not None:
        instance.archived_at = None
