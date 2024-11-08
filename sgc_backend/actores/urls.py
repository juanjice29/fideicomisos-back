from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    
    path('actor/<str:tipo_id>/<str:nro_id>/',ActorView.as_view(),name="actor_view"),
    path('actores/',ActorListView.as_view(),name="actor_list"),
    path('futuroc/<str:tipo_id>/<str:nro_id>/',FuturoCompradorView.as_view(),name="futuroc_view"),
    path('futurosc/',FuturoCompradorListView.as_view(),name="futuroc_list"),
    path('actores-fidei-excel/<str:codigo_SFC>/',ActoresByFideiFileUploadView.as_view(),name="cargar_actores_excel_by_fidei"),
    path('actores-excel/',ActoresFileUploadView.as_view(),name="cargar_actores_excel"),
    #path('upload/', FileUploadView.as_view(), name='upload_file'),
    #path('actordecontratolist/<str:codigo_sfc>/', ActorDeContratoListView.as_view(), name='actordecontrato-list'),
    #path('actordecontratolist/', ActorDeContratoListAllView.as_view(), name='actordecontrato-list-all'),
    #path('actor_de_contrato_excel/', ActorDeContratoViewExcel.as_view(), name='actor_de_contrato_excel'),
    #path('actorfidelist/', ListFideicomisosOfActorView.as_view(), name='actordecontratfide-list-all'),
    #path('tipoactordecontrato/', TipoActorDeContratoListView.as_view(), name='tipoactordecontrato-list'),
    #path('crearactordecontrato/', ActorDeContratoView.as_view(), name='crearactordecontrato'),    
    #path('add-fide/', AddFideicomisosToActorView.as_view(), name='addfideact'),
    #path('actor/<str:nro_ident>/',GetActorView.as_view(), name='checkactor'),
    #path('updateactor/', UpdateActorView.as_view(), name='update-actor'),
]