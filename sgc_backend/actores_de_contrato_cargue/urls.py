from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='upload_file'),
    path('actordecontratolist/<str:codigo_sfc>/', ActorDeContratoListView.as_view(), name='actordecontrato-list'),
    path('actordecontratolist/', ActorDeContratoListAllView.as_view(), name='actordecontrato-list-all'),
    path('actorfidelist/', ListFideicomisosOfActorView.as_view(), name='actordecontratfide-list-all'),
    path('tipoactordecontrato/', TipoActorDeContratoListView.as_view(), name='tipoactordecontrato-list'),
    path('crearactordecontrato/', ActorDeContratoCreateView.as_view(), name='crearactordecontrato'),
    path('añadirfide/', AddFideicomisosToActorView.as_view(), name='addfideact'),
    #path('encargo/', EncargoListView.as_view(), name='encargo-list'), #http://127.0.0.1:8000/actores/encargo/?CodigoSFC=116788
    path('actordecontrato/<int:id>/', ActorDeContratoUpdateView.as_view(), name='actordecontrato-update'),
    path('actordecontrato/<int:id>/delete/', ActorDeContratoDeleteView.as_view(), name='actordecontrato-delete'),
]