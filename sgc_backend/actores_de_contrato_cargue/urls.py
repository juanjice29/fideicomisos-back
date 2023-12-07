from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .views import ActorDeContratoViewSet

router = DefaultRouter()
router.register(r'actordecontrato', ActorDeContratoViewSet)

urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
    path('', include(router.urls)),
]