"""
Django ORM models for Todos
"""
import math
import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
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
    version = models.IntegerField(default=1)
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
    Increment version for updates
    """
    if instance.completed and instance.completed_at is None:
        instance.completed_at = timezone.now()
    if not instance.completed and instance.completed_at is not None:
        instance.completed_at = None
    if instance.archived and instance.archived_at is None:
        instance.archived_at = timezone.now()
    if not instance.archived and instance.archived_at is not None:
        instance.archived_at = None

    # Increment version on update (but not on create)
    if instance.pk is not None:
        instance.version = F('version') + 1

    if instance.order_rank is None:
        order_metadata = RankOrderMetadata.objects.first()
        if order_metadata is not None:
            instance.order_rank = (order_metadata.max_rank +
                                   RANK_ORDER_DEFAULT_STEP)


def validate_label_name(value):
    """
    Validator for label names.
    Ensures name contains only alphanumeric characters, spaces,
    and common punctuation.
    """
    if not value or not value.strip():
        raise ValidationError('Label name cannot be empty or whitespace only.')

    if len(value) > 50:
        raise ValidationError('Label name cannot exceed 50 characters.')

    # Allow alphanumeric, spaces, and common punctuation
    pattern = r'^[a-zA-Z0-9\s\-_.,!?()\[\]]+$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Label name can only contain letters, numbers, spaces, '
            'and common punctuation (- _ . , ! ? ( ) [ ]).')


class LabelModel(models.Model):
    """
    A label for todos
    """
    name = models.TextField(
        validators=[validate_label_name],
        unique=True,
        help_text=('Label name (max 50 characters, '
                   'alphanumeric + spaces + common punctuation)'))
    todo_set = models.ManyToManyField(
        TodoModel,
        related_name="labels",
        blank=True,
        editable=False,
    )

    def __str__(self):
        return self.name

    def clean(self):
        """
        Validate the model before saving.
        Strips whitespace and checks for case-insensitive duplicates.
        """
        super().clean()

        # Strip whitespace
        if self.name:
            self.name = self.name.strip()

        # Check for empty after stripping
        if not self.name:
            raise ValidationError(
                {'name': 'Label name cannot be empty or whitespace only.'})

        # Check for case-insensitive duplicates
        existing = LabelModel.objects.filter(name__iexact=self.name)
        if self.pk:
            existing = existing.exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError({
                'name': (f'A label with name "{self.name}" '
                         f'already exists (case-insensitive).')
            })


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
