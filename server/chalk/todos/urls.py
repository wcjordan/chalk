"""
Url routing for reinforcement learning models
"""
from django.urls import include, path
from rest_framework import routers

from chalk.todos import views

router = routers.DefaultRouter()
router.register('todos', views.TodoViewSet)
router.register('labels', views.LabelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
