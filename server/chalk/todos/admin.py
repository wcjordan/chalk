"""
Django admin config for Todos
"""
from django import forms
from django.contrib import admin
from django.db import models as django_models
from simple_history.admin import SimpleHistoryAdmin

from chalk.todos import models


class LabelAdmin(admin.ModelAdmin):
    """
    Admin interface for managing custom labels.
    Labels can be created via admin UI and will automatically appear
    in the React app's label picker.
    """
    list_display = ['name', 'id', 'todo_count']
    search_fields = ['name']
    ordering = ['name']
    readonly_fields = ['id']

    formfield_overrides = {
        django_models.TextField: {
            'widget': forms.TextInput(attrs={
                'size': '50',
                'maxlength': '50'
            })
        },
    }

    @admin.display(description='Todo Count')
    def todo_count(self, obj):
        """
        Display the count of todos associated with this label.
        """
        return obj.todo_set.count()


admin.site.register(models.TodoModel, SimpleHistoryAdmin)
admin.site.register(models.LabelModel, LabelAdmin)
