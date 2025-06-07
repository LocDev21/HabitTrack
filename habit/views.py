from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import HabitudeForm 
from django.contrib.auth.decorators import login_required
from .models import Habitude, Suivi
from datetime import date 

# Create your views here.
#-----------------------------------------Vue pour l'inscription--------------------------------------------------

def inscription(request):
    if request.method == 'POST' : 
        form = UserCreationForm(request.POST) # form prend les informations sur le formulaire que l'utilisateur renvoie
        if form.is_valid(): 
            user = form.save() # Si ce formulaire est valide on le sauvegarde
            login(request,user) # Connecter l'utilisateur après inscription  
            messages.success(request, 'Vous êtes inscrit(e), Bienvenue !') # Message de bienvenue

            return redirect('dashboard') # Dirige vers le tableau de bord
    else:
            form = UserCreationForm() # Méthode Get c'est à dire première visite

    return render(request, 'registration/inscription.html', {'form': form})

#-----------------------------------------Vue pour la connnexion----------------------------------------------------

def connexion (request):
     if request.method == 'POST':
          username = request.POST ['username']
                                                # Récupération des données du formulaire
          password = request.POST ['password']
          user = authenticate(request,username=username,password=password)

          if user is not None:
            login(request, user)
            messages.success(request, 'Connexion réussie !')

            return redirect('dashboard')
          else:
           
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.') 
    
     return render(request, 'registration/connexion.html')

#-----------------------------------------Vue pour la déconnexion----------------------------------------------------

def  deconnexion (request):
    logout(request)
    messages.success('Déconnexion réussie !')
    return redirect ('connexion')

#-----------------------------------------Vue pour ajouter une habitude----------------------------------------------------

@login_required
def ajouter_habitude (request):
    if request.method=='POST':
        form = HabitudeForm(request.POST)
        if form.is_valid():
            Habitude=form.save(commit=False) #faire attendre l'enregistremement
            Habitude.utilisateur=request.user #Lier l'utilisateur à l'habitude
            Habitude.save()
            return redirect ('dashboard')
    else:
        form = HabitudeForm()
    return render (request,'ajouter_habitude.html',{'form':form})

#-----------------------------------------Vue pour le dashboard----------------------------------------------------

@login_required
def dashboard (request):
    habitudes = Habitude.objects.filter(utilisateur=request.user)
    return render (request,'dashboard.html',{'habitudes':habitudes})

#-----------------------------------------Vue pour modifier l'habitude----------------------------------------------------

@login_required
def modifier_habitude(request, id):
    habitude = get_object_or_404(Habitude, pk=id, utilisateur=request.user)

    if request.method == 'POST':
        form = HabitudeForm(request.POST, instance=habitude)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = HabitudeForm(instance=habitude)

    return render(request, 'modifier_habitude.html', {'form': form})

#-----------------------------------------Vue pour suprimer l'habitude----------------------------------------------------

@login_required
def supprimer_habitude(request, id):
    habitude = get_object_or_404(Habitude, pk=id, utilisateur=request.user)
    habitude.delete()
    return redirect('dashboard')

#-----------------------------------------Vue pour marquer une habitude comme faite----------------------------------------------------

@login_required
def marquer_habitude(request, id):
    habitude = get_object_or_404(Habitude, pk=id, utilisateur=request.user)
    
    # Vérifier si un suivi existe déjà pour aujourd'hui
    suivi, created = Suivi.objects.get_or_create(
        habitude=habitude,
        date=date.today(),
        defaults={'fait': True}
    )
    
    if not created:
        suivi.fait = True
        suivi.save()
    
    return redirect('dashboard')