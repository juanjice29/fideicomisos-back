from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='upload_file'),
    path('actordecontratolist/<str:codigo_sfc>/', ActorDeContratoListView.as_view(), name='actordecontrato-list'),
    path('actordecontratolist/', ActorDeContratoListAllView.as_view(), name='actordecontrato-list-all'),
    path('actorfidelist/', ListFideicomisosOfActorView.as_view(), name='actordecontratfide-list-all'),
    path('tipoactordecontrato/', TipoActorDeContratoListView.as_view(), name='tipoactordecontrato-list'),
    path('crearactordecontrato/', ActorDeContratoView.as_view(), name='crearactordecontrato'),
    path('añadirfide/', AddFideicomisosToActorView.as_view(), name='addfideact')
]