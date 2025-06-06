from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


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

            