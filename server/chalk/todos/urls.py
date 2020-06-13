"""
Url routing for reinforcement learning models
"""
from django.urls import include, path
from rest_framework import routers

from chalk.todos import views

router = routers.DefaultRouter()
router.register('todos', views.TodoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
