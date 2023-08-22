"""
App for Todos
"""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class TodosConfig(AppConfig):
    """
    Todos App
    """
    name = 'chalk.todos'

    def ready(self):
        # pylint: disable=import-outside-toplevel
        from chalk.todos.signals import rebalance_rank_order
        post_migrate.connect(rebalance_rank_order, sender=self)
