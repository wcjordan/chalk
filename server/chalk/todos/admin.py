"""
Django admin config for Todos
"""
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from chalk.todos import models

admin.site.register(models.TodoModel, SimpleHistoryAdmin)
