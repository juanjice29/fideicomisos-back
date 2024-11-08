from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from public import views

urlpatterns = [
    path('',views.IndexView.as_view()),
    path('api/restricted', views.RestrictedView.as_view(), name='restricted'),
    path('tipos-de-documento/', views.TipoDeDocumentoListView.as_view(), name='tipos_de_documento_list'),
    path('tipos-de-actor/', views.TipoDeActorListView.as_view(), name='tipos_de_actor_list'),
    path('periodos-trimestral/', views.PeriodoTrimestralListView.as_view(), name='periodos_trimestral'),
    path('params-generic/<str:nombre>/', views.GenericParamDetailView.as_view(), name='params_generic'),
    
]

urlpatterns = format_suffix_patterns(urlpatterns)

