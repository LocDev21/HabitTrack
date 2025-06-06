from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.connexion, name= 'connexion'),
    path('inscription/', views.inscription, name='inscription' ),
    path('deconnexion/', views.deconnexion, name='deconnexion')
]
