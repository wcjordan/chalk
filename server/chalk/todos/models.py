"""
Django ORM models for Todos
"""
import math

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from simple_history.models import HistoricalRecords

from chalk.todos.consts import RANK_ORDER_DEFAULT_STEP


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
    order_rank = models.BigIntegerField(null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.description

    class Meta:
        ordering = ['order_rank', 'created_at']


@receiver(pre_save, sender=TodoModel)
# pylint: disable=unused-argument
def update_derived_fields(sender, instance, *args, **kwargs):
    """
    Before saving, update timestamps if necessary
    Also set the order rank if it is not set
    """
    if instance.completed and instance.completed_at is None:
        instance.completed_at = timezone.now()
    if not instance.completed and instance.completed_at is not None:
        instance.completed_at = None
    if instance.archived and instance.archived_at is None:
        instance.archived_at = timezone.now()
    if not instance.archived and instance.archived_at is not None:
        instance.archived_at = None

    if instance.order_rank is None:
        order_metadata = RankOrderMetadata.objects.first()
        if order_metadata is not None:
            instance.order_rank = (order_metadata.max_rank +
                                   RANK_ORDER_DEFAULT_STEP)


class LabelModel(models.Model):
    """
    A label for todos
    """
    name = models.TextField()
    todo_set = models.ManyToManyField(TodoModel, related_name="labels")

    def __str__(self):
        return self.name


class RankOrderMetadata(models.Model):
    """
    Metadata about the closest entries in the rank ordering
    Useful for deciding if a rebalance is necessary
    """
    closest_rank_min = models.BigIntegerField(null=True)
    closest_rank_max = models.BigIntegerField(null=True)
    closest_rank_distance = models.BigIntegerField(null=True)
    closest_rank_steps = models.IntegerField(null=True)
    last_rebalanced_at = models.DateTimeField(null=True)
    last_rebalance_duration = models.FloatField(null=True)
    max_rank = models.BigIntegerField(null=True)
    history = HistoricalRecords()

    def __str__(self):
        return (f"[{self.closest_rank_min}-{self.closest_rank_max}] "
                f"({self.closest_rank_steps}) last rebalanced at: "
                f"{self.last_rebalanced_at}")


@receiver(pre_save, sender=RankOrderMetadata)
# pylint: disable=unused-argument
def update_order_metadata(sender, instance, *args, **kwargs):
    """
    Before saving, update compute steps
    """
    instance.closest_rank_distance = (instance.closest_rank_max -
                                      instance.closest_rank_min)

    if instance.closest_rank_distance == 0:
        instance.closest_rank_steps = 0
    else:
        instance.closest_rank_steps = math.floor(
            math.log2(instance.closest_rank_distance))
