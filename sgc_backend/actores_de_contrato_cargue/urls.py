from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .views import EncargoListView

urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
    path('actordecontratolist/', ActorDeContratoListView.as_view(), name='actordecontrato-list'),
    path('tipoactordecontrato/', TipoActorDeContratoListView.as_view(), name='tipoactordecontrato-list'),
    path('crearactordecontrato/', ActorDeContratoCreateView.as_view(), name='crearactordecontrato'),
    path('encargo/', EncargoListView.as_view(), name='encargo-list'), #http://127.0.0.1:8000/actores/encargo/?CodigoSFC=116788
    path('actordecontrato/<int:id>/', ActorDeContratoUpdateView.as_view(), name='actordecontrato-update'),
    path('actordecontrato/<int:id>/delete/', ActorDeContratoDeleteView.as_view(), name='actordecontrato-delete'),
]