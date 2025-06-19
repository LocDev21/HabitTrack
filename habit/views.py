# habit/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import HabitudeForm
from .models import Habitude, Suivi, Badge
from datetime import date, timedelta
from django.utils import timezone
from django.http import Http404, JsonResponse 
import json 

# --- Authentification et gestion des utilisateurs ---

def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenue, {username} !")
            return redirect('dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'connexion.html')

def inscription(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Votre compte a été créé avec succès et vous êtes maintenant connecté !")
            # Créer les badges initiaux pour le nouvel utilisateur
            Badge.objects.create(utilisateur=user, nom_badge='Débutant', description_badge='Première connexion à HabitTrack !')
            return redirect('dashboard')
        else:
            # Afficher les erreurs du formulaire si la validation échoue
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur sur le champ '{field}': {error}")
    else:
        form = UserCreationForm()
    return render(request, 'inscription.html', {'form': form})

@login_required
def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('connexion')

# --- Gestion des habitudes ---

@login_required
def ajouter_habitude(request):
    if request.method == 'POST':
        form = HabitudeForm(request.POST)
        if form.is_valid():
            habitude = form.save(commit=False)
            habitude.utilisateur = request.user
            habitude.save()
            messages.success(request, f"L'habitude '{habitude.titre}' a été ajoutée avec succès !")
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur sur le champ '{field}': {error}")
    else:
        form = HabitudeForm()
    return render(request, 'ajouter_habitude.html', {'form': form})

@login_required
def modifier_habitude(request, id):
    habitude = get_object_or_404(Habitude, pk=id, utilisateur=request.user)
    if request.method == 'POST':
        form = HabitudeForm(request.POST, instance=habitude)
        if form.is_valid():
            form.save()
            messages.success(request, f"L'habitude '{habitude.titre}' a été modifiée avec succès !")
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur sur le champ '{field}': {error}")
    else:
        form = HabitudeForm(instance=habitude)
    return render(request, 'modifier_habitude.html', {'form': form, 'habitude': habitude})

@login_required
def supprimer_habitude(request, id):
    habitude = get_object_or_404(Habitude, pk=id, utilisateur=request.user)
    titre_habitude = habitude.titre
    habitude.delete()
    messages.info(request, f"L'habitude '{titre_habitude}' a été supprimée.")
    return redirect('dashboard')

# -----------------------------------------Vue pour marquer une habitude comme faite----------------------------------------------------
@login_required
def marquer_habitude(request, id):
    if request.method == 'POST':
        habitude = get_object_or_404(Habitude, pk=id, utilisateur=request.user)
        today = date.today()

        try:
            data = json.loads(request.body)
            is_completed = data.get('is_completed')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        suivi, created = Suivi.objects.get_or_create(
            habitude=habitude,
            date=today,
            defaults={'fait': is_completed}
        )

        if not created:
            if suivi.fait != is_completed: # Si l'état change
                suivi.fait = is_completed
                suivi.save()
                message = f"L'habitude '{habitude.titre}' a été marquée comme {'faite' if is_completed else 'non faite'} pour aujourd'hui !"
                messages.success(request, message)
            else:
                message = f"L'habitude '{habitude.titre}' est déjà marquée comme {'faite' if is_completed else 'non faite'} pour aujourd'hui."
                messages.info(request, message)
        else:
            message = f"L'habitude '{habitude.titre}' a été marquée comme {'faite' if is_completed else 'non faite'} pour aujourd'hui !"
            messages.success(request, message)
        
        # Mettre à jour derniere_realisation sur le modèle Habitude
        if is_completed:
            habitude.derniere_realisation = today
        else:
            # Si l'habitude est décochée pour aujourd'hui, on ne peut pas simplement mettre null.
            # Il faudrait trouver la dernière date où elle a été faite (si elle existe)
            last_done_suivi = Suivi.objects.filter(
                habitude=habitude, fait=True, date__lt=today
            ).order_by('-date').first()
            habitude.derniere_realisation = last_done_suivi.date if last_done_suivi else None
        habitude.save()


        return JsonResponse({'success': True, 'message': message})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405) # Méthode non autorisée si ce n'est pas POST


# -----------------------------------------Fonction pour vérifier et attribuer les badges----------------------------------------------------

def check_and_award_badges(request):
    user = request.user
    today = date.today()

    # Récupérer toutes les habitudes de l'utilisateur
    habitudes = Habitude.objects.filter(utilisateur=user)

    for habitude in habitudes:
        # --- Logique pour le badge "Assidu" (7 jours consécutifs) ---
        consecutive_days = 0
        current_date_for_streak = today
        while True:
            suivi_du_jour = Suivi.objects.filter(habitude=habitude, date=current_date_for_streak, fait=True).first()
            if suivi_du_jour:
                consecutive_days += 1
                current_date_for_streak -= timedelta(days=1)
            else:
                break
        
        if consecutive_days >= 7:
            badge_assidu, created = Badge.objects.get_or_create(
                utilisateur=user,
                nom_badge="Assidu",
                defaults={'description_badge': "7 jours consécutifs de suivi d'une habitude."}
            )
            if created:
                messages.success(request, "Félicitations ! Vous avez gagné le badge 'Assidu' pour 7 jours consécutifs de suivi !")
        
        # --- Logique pour le badge "Persévérant" (30 jours consécutifs) ---
        if consecutive_days >= 30:
            badge_perseverant, created = Badge.objects.get_or_create(
                utilisateur=user,
                nom_badge="Persévérant",
                defaults={'description_badge': "30 jours consécutifs de suivi d'une habitude."}
            )
            if created:
                messages.success(request, "Incroyable ! Vous avez gagné le badge 'Persévérant' pour 30 jours consécutifs !")

    # --- Logique pour le badge "Polyvalent" (5 habitudes actives) ---
    active_habits_count = habitudes.count()
    if active_habits_count >= 5:
        badge_polyvalent, created = Badge.objects.get_or_create(
            utilisateur=user,
            nom_badge="Polyvalent",
            defaults={'description_badge': "Gestion de 5 habitudes ou plus simultanément."}
        )
        if created:
            messages.success(request, "Impressionnant ! Vous avez gagné le badge 'Polyvalent' pour gérer 5 habitudes ou plus !")

    # --- Logique pour le badge "Maître des Habitudes" (10 habitudes actives) ---
    if active_habits_count >= 10:
        badge_maitre, created = Badge.objects.get_or_create(
            utilisateur=user,
            nom_badge="Maître des Habitudes",
            defaults={'description_badge': "Gestion de 10 habitudes ou plus simultanément."}
        )
        if created:
            messages.success(request, "Exceptionnel ! Vous êtes un 'Maître des Habitudes' en gérant 10 habitudes ou plus !")


# -----------------------------------------Vue du Tableau de bord----------------------------------------------------
@login_required
def dashboard(request):
    user = request.user
    
    # Appeler la fonction de vérification et d'attribution des badges
    check_and_award_badges(request)

    # Trier les habitudes par fréquence (quotidien d'abord, puis hebdomadaire)
    # Puis par date de création (plus récentes d'abord)
    habitudes_quotidiennes = Habitude.objects.filter(utilisateur=user, frequence='quotidien').order_by('-date_creation')
    habitudes_hebdomadaires = Habitude.objects.filter(utilisateur=user, frequence='hebdomadaire').order_by('-date_creation')
    
    # Concaténer les QuerySets en une liste pour l'itération dans le template
    habitudes = list(habitudes_quotidiennes) + list(habitudes_hebdomadaires)

    # Dictionnaire pour stocker les statistiques pour chaque habitude
    stats = {}
    today = date.today()

    for habitude in habitudes:
        # Récupérer les 7 derniers jours (du plus ancien au plus récent)
        jours = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)] # Dates des 7 derniers jours (inclut aujourd'hui)
        donnees = []
        
        # Récupérer les suivis pour cette habitude sur les 7 derniers jours
        suivis_7jours = Suivi.objects.filter(
            habitude=habitude,
            date__gte=today - timedelta(days=6),
            date__lte=today
        ).order_by('date')

        suivis_map = {s.date.isoformat(): s.fait for s in suivis_7jours}

        for j in jours:
            donnees.append(1 if suivis_map.get(j, False) else 0)

        # Calcul des jours consécutifs
        consecutive_days = 0
        current_date_for_streak = today
        while True:
            suivi_du_jour = Suivi.objects.filter(habitude=habitude, date=current_date_for_streak).first()
            if suivi_du_jour and suivi_du_jour.fait:
                consecutive_days += 1
                current_date_for_streak -= timedelta(days=1)
            else:
                break
        
        stats[habitude.id] = {
            'jours': jours,
            'donnees': donnees,
            'consecutive_days': consecutive_days,
            'derniere_realisation': habitude.derniere_realisation.isoformat() if habitude.derniere_realisation else None,
            'aujourd_hui_fait': Suivi.objects.filter(habitude=habitude, date=today, fait=True).exists() # Ajout pour l'état de la checkbox
        }

    # Récupérer les badges de l'utilisateur
    badges = Badge.objects.filter(utilisateur=user).order_by('nom_badge') # Tri alphabétique ou par un champ 'ordre' si défini

    context = {
        'habitudes': habitudes,
        'stats': stats,
        'today': today, # Passez 'today' au contexte pour l'affichage ou la logique JS
        'badges': badges,
    }
    return render(request, 'dashboard.html', context)


# -----------------------------------------Vue du Blog ----------------------------------------------------

def blog_view(request):
    # Liste simulée d'articles de blog
    articles = [
        {
            'slug': 'alimentation-saine-booster-productivite', # Nouveau slug
            'titre': 'Alimentation Saine : Votre Carburant pour une Productivité Maximale', # Nouveau titre
            'extrait': 'Découvrez comment une alimentation équilibrée peut non seulement améliorer votre santé physique et mentale, mais aussi décupler votre productivité au quotidien.', # Nouvel extrait
            'image': 'images/alimentation-saine.jpeg', # Nouvelle image (assurez-vous que cette image existe dans votre dossier static/images)
        },
        {
            'slug': 'cyclisme-energie-serenite',
            'titre': 'Le Cyclisme : Votre Passeport pour l\'Énergie et la Sérénité',
            'extrait': 'Découvrez comment le cyclisme peut transformer votre routine, améliorer votre endurance et réduire le stress.',
            'image': 'images/velo.jpeg', # Chemin relatif à static
        },
        {
            'slug': 'matin-productif-cle-du-succes',
            'titre': 'Matin Productif : La Clé du Succès au Quotidien',
            'extrait': 'Apprenez à structurer vos matinées pour maximiser votre productivité et votre bien-être général.',
            'image': 'images/productive-morning.jpeg',
        },
        {
            'slug': 'evader-nature-recharge-esprit',
            'titre': 'S\'évader dans la Nature : Recharger Votre Esprit et Améliorer Votre Productivité',
            'extrait': 'Explorez les bienfaits de la nature sur la réduction du stress et l\'augmentation de la concentration.',
            'image': 'images/nature.jpeg',
        },
        {
            'slug': 'yoga-meditation-pleine-conscience',
            'titre': 'Yoga et Méditation : Ancrer la Pleine Conscience dans Votre Journée',
            'extrait': 'Découvrez les pratiques du yoga et de la méditation pour équilibrer le corps et l\'esprit et réduire l\'anxiété.',
            'image': 'images/yoga2.jpeg',
        },
    ]
    return render(request, 'blog.html', {'articles': articles})

def blog_detail_view(request, slug):
    """
    Vue pour afficher les détails d'un article de blog spécifique.
    Pour l'instant, c'est une simulation. Si vous aviez un modèle Blog Article :
    article = get_object_or_404(ArticleDeBlog, slug=slug)
    """
    
    articles_simules = {
        'alimentation-saine-booster-productivite': { # Nouvelle entrée pour l'alimentation saine
            'titre': 'Alimentation Saine : Votre Carburant pour une Productivité Maximale',
            'contenu': """
                Une alimentation saine n'est pas seulement essentielle pour votre bien-être physique, elle est aussi
                un pilier fondamental de votre productivité et de votre clarté mentale. En fournissant à votre corps
                les nutriments dont il a besoin, vous optimisez vos niveaux d'énergie, améliorez votre concentration,
                et réduisez la fatigue et le stress. Oubliez les fringales de l'après-midi et les coups de barre ;
                une alimentation équilibrée vous assure une énergie stable tout au long de la journée.

                Intégrer des habitudes alimentaires saines, comme la consommation de fruits et légumes frais, de protéines
                maigres et de grains entiers, peut sembler un défi. Cependant, avec HabitTrack, vous pouvez suivre
                facilement ces nouvelles habitudes. Fixez-vous des objectifs, comme "manger cinq portions de légumes par jour"
                ou "boire 2 litres d'eau", et observez vos progrès. Laissez HabitTrack vous aider à transformer votre
                alimentation en un véritable atout pour une vie plus saine et une productivité accrue.
                """
        },
        'cyclisme-energie-serenite': {
            'titre': 'Le Cyclisme : Votre Passeport pour l\'Énergie et la Sérénité',
            'contenu': """
                Le cyclisme est bien plus qu'une simple activité physique ; c'est une habitude qui peut révolutionner votre quotidien.
                En l'intégrant à votre routine, vous constaterez non seulement une amélioration de votre endurance cardiovasculaire,
                mais aussi une diminution significative du stress. Le simple fait de pédaler en plein air, de sentir le vent
                sur votre visage et de voir défiler les paysages, offre une évasion mentale bienvenue. C'est un excellent moyen
                de rester actif, de renforcer vos muscles et d'améliorer votre humeur.
                HabitTrack vous aide à suivre vos sorties à vélo, à visualiser vos progrès et à maintenir cette habitude saine.
                Fixez-vous des objectifs de distance, de durée ou de fréquence, et laissez l'application vous motiver à chaque coup de pédale.
                """
        },
        'matin-productif-cle-du-succes': {
            'titre': 'Matin Productif : La Clé du Succès au Quotidien',
            'contenu': """
                Un matin bien commencé est un matin à moitié gagné. Adopter une routine matinale productive est une habitude
                qui peut transformer l'ensemble de votre journée. Que ce soit se lever tôt, méditer, faire de l'exercice léger,
                ou planifier sa journée, chaque action contribue à poser les bases d'une journée réussie. Une routine matinale
                permet de réduire la procrastination, d'améliorer la concentration et de commencer la journée avec un sentiment
                d'accomplissement.
                Avec HabitTrack, vous pouvez structurer et suivre les éléments de votre routine matinale. Marquez chaque tâche
                comme accomplie, observez vos séries de succès et laissez l'application vous encourager à maintenir ces habitudes
                qui boostent votre productivité et votre bien-être général.
                """
        },
        'evader-nature-recharge-esprit': {
            'titre': 'S\'évader dans la Nature : Recharger Votre Esprit et Améliorer Votre Productivité',
            'contenu': """
                Dans notre monde trépidant, prendre le temps de se connecter à la nature est une habitude souvent sous-estimée
                mais incroyablement bénéfique. Que ce soit une courte promenade dans un parc, une randonnée en forêt, ou simplement
                passer du temps dans votre jardin, la nature offre une multitude de bienfaits : réduction du stress, l'amélioration
                de l'humeur et l'augmentation de la capacité de concentration. Faites de "passer du temps en nature" une habitude
                régulière avec HabitTrack, et observez comment cette simple pratique peut revitaliser votre esprit et votre corps,
                vous rendant plus productif et serein.
                """
        },
        'yoga-meditation-pleine-conscience': {
            'titre': 'Yoga et Méditation : Ancrer la Pleine Conscience dans Votre Journée',
            'contenu': """
                Le yoga et la méditation ne sont pas de simples exercices, mais des chemins vers une plus grande pleine conscience
                et un équilibre intérieur. En intégrant ces pratiques à votre routine quotidienne avec HabitTrack, vous pouvez
                améliorer votre flexibilité, renforcer votre corps, calmer votre esprit et réduire significativement le niveau
                de stress. Ces habitudes développent également la discipline et la persévérance, des qualités essentielles
                pour atteindre d'autres objectifs dans votre vie. Suivez vos sessions, constatez vos progrès et laissez
                HabitTrack vous guider vers une vie plus équilibrée et consciente.
                """
        }
    }
    
    article = articles_simules.get(slug)
    if not article:
        raise Http404("Article de blog non trouvé.")
    return render(request, 'blog_detail.html', {'article': article})