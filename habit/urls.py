from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.connexion, name= 'connexion'),
    path('inscription/', views.inscription, name='inscription' ),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('ajouter/', views.ajouter_habitude, name='ajouter_habitude'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('modifier/<int:id>/',views.modifier_habitude, name='modifier_habitude'),
    path('supprimer/<int:id>/',views.supprimer_habitude, name='supprimer_habitude'),
    path('marquer/<int:id>/', views.marquer_habitude, name='marquer_habitude'),

]
