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
        from chalk.todos.signals import evaluate_rank_rebalance
        post_migrate.connect(evaluate_rank_rebalance, sender=self)
