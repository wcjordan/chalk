"""
Django admin config for Todos
"""
from django.contrib import admin

from chalk.todos import models

admin.site.register(models.TodoModel)
