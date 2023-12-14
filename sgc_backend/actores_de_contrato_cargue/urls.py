from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .views import EncargoListView

urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
    path('tipoactordecontrato/', TipoActorDeContratoListView.as_view(), name='tipoactordecontrato-list'),
    path('crearactordecontrato/', ActorDeContratoCreateView.as_view(), name='crearactordecontrato'),
    path('encargo/<int:FideicomisoAsociado>/', EncargoListView.as_view(), name='encargo-list'),
    path('actordecontrato/<int:id>/', ActorDeContratoUpdateView.as_view(), name='actordecontrato-update'),
    path('actordecontrato/<int:id>/delete/', ActorDeContratoDeleteView.as_view(), name='actordecontrato-delete'),
]