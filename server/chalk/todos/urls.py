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
    path('auth/', views.auth),
    path('auth_callback/', views.auth_callback),
    path('auth_test/', views.auth_test),
    path('healthz/', views.healthz),
    path('status/', views.status),
    path('', include(router.urls)),
]
