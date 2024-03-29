"""
Signal handlers for handling todo updates and rebalancing the rank order
"""
import time

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from chalk.todos.consts import (RANK_ORDER_DEFAULT_STEP,
                                RANK_ORDER_INITIAL_STEP, RANK_ORDER_MAX)
from chalk.todos.models import RankOrderMetadata, TodoModel


@receiver(post_save, sender=TodoModel)
# pylint: disable=unused-argument
def update_rank_metadata(sender, instance, *args, **kwargs):
    """
    Update the max rank and closest rank order metadata if necessary after any
    Todo is saved.
    """
    order_metadata = RankOrderMetadata.objects.first()
    if (order_metadata is None or
            instance.order_rank <= order_metadata.max_rank):
        return

    order_metadata.max_rank = instance.order_rank

    # Check if the distance to the largest big int is the closest rank distance
    distance = RANK_ORDER_MAX - order_metadata.max_rank
    if distance < order_metadata.closest_rank_distance:
        order_metadata.closest_rank_min = order_metadata.max_rank
        order_metadata.closest_rank_max = RANK_ORDER_MAX
    order_metadata.save()


@receiver(post_save, sender=RankOrderMetadata)
# pylint: disable=unused-argument
def evaluate_rank_rebalance(**kwargs):
    """
    Rebalance the rank order if necessary after checking the RankOrderMetadata
    Looks to see if the closest 2 items can only support a small number of
    inserts between them.
    """
    order_metadata = RankOrderMetadata.objects.first()
    if (order_metadata and order_metadata.closest_rank_steps and
            order_metadata.closest_rank_steps > 2):
        return

    rebalance_rank_order()


def rebalance_rank_order():
    """
    Rebalance the rank order and update the RankOrderMetadata
    """
    start_time = time.time()
    todos = TodoModel.objects.select_for_update().filter(archived=False)
    curr_rank_order = RANK_ORDER_INITIAL_STEP
    with transaction.atomic():
        for todo in todos:
            todo.order_rank = curr_rank_order
            curr_rank_order += RANK_ORDER_DEFAULT_STEP
        TodoModel.objects.bulk_update(todos, ['order_rank'])

        closest_rank_max = RANK_ORDER_INITIAL_STEP + RANK_ORDER_DEFAULT_STEP
        order_metadata, _ = RankOrderMetadata.objects.update_or_create(
            defaults={
                'closest_rank_min': RANK_ORDER_INITIAL_STEP,
                'closest_rank_max': closest_rank_max,
                # Set closest_rank_steps to None to avoid
                # an infinite loop from re-evaluation
                'closest_rank_steps': None,
                'last_rebalanced_at': timezone.now(),
                'last_rebalance_duration': time.time() - start_time,
                'max_rank': curr_rank_order - RANK_ORDER_DEFAULT_STEP,
            },)
        order_metadata.save()
