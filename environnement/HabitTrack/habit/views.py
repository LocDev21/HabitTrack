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


from django.http import Http404

def blog_detail_view(request, slug):
    """
    Vue pour afficher les détails d'un article de blog spécifique.
    Pour l'instant, c'est une simulation. Si vous aviez un modèle Blog Article :
    article = get_object_or_404(ArticleDeBlog, slug=slug)
    """
    
    articles_simules = {
        'cyclisme-energie-serenite': {
            'titre': 'Le Cyclisme : Votre Passeport pour l\'Énergie et la Sérénité',
            'contenu': """
                Le cyclisme est bien plus qu'une simple activité physique ; c'est une habitude qui peut révolutionner votre quotidien.
                En l'intégrant à votre routine, vous constaterez non seulement une amélioration de votre endurance cardiovasculaire,
                mais aussi une diminution significative du stress. Le simple fait de pédaler en plein air, de sentir le vent
                sur votre visage et de voir défiler les paysages, offre une évasion mentale bienvenue. C'est un moment pour
                vous-même, propice à la réflexion ou simplement à la déconnexion. HabitTrack vous permet de suivre vos
                sorties, vos distances et votre régularité, transformant chaque coup de pédale en une étape vers vos objectifs
                de bien-être. De plus, opter pour le vélo comme moyen de transport réduit votre empreinte carbone et vous fait
                découvrir votre environnement sous un nouvel angle. Commencez petit, quelques kilomètres par semaine,
                et augmentez progressivement. Vous serez étonné des bénéfices cumulatifs sur votre corps et votre esprit.
            """,
            'image': 'velo.jpeg'
        },
        'pouvoir-mots-lecture': {
            'titre': 'Le Pouvoir des Mots : Cultiver l\'Habitude de la Lecture',
            'contenu': """
                Dans un monde saturé d'informations éphémères, la lecture demeure un pilier fondamental pour le développement personnel.
                Cultiver l'habitude de lire, même quelques pages par jour, peut transformer votre esprit. La lecture nourrit la curiosité,
                élargit les perspectives, améliore la concentration et enrichit le vocabulaire. C'est une forme de méditation active
                qui permet de s'immerger dans de nouvelles idées, cultures et histoires. Que ce soit un roman captivant, un livre
                de non-fiction enrichissant, ou un recueil de poésie, chaque moment passé à lire est un investissement en vous-même.
                HabitTrack vous aide à maintenir cette précieuse habitude en vous permettant de définir des objectifs de lecture
                quotidiens ou hebdomadaires, et de suivre votre progression. Voyez comment cette habitude simple peut ouvrir des portes
                vers une connaissance infinie et une compréhension plus profonde du monde et de vous-même.
            """,
            'image': 'foret3.jpeg'
        },
        'evader-nature-recharge-esprit': {
            'titre': 'S\'Évader en Nature : L\'Habitude qui Recharge l\'Esprit',
            'contenu': """
                La vie moderne nous maintient souvent enfermés, déconnectés de l'environnement naturel. Pourtant, passer du temps en nature
                est une habitude simple mais incroyablement puissante pour notre bien-être. Une promenade en forêt, un moment au bord
                d'un lac, ou même simplement s'asseoir dans un parc peut réduire le stress, améliorer l'humeur et augmenter la clarté mentale.
                La "thérapie par la nature" ou "bain de forêt" est reconnue pour ses bienfaits sur la santé physique et psychologique.
                En faisant de cette évasion une habitude régulière, vous créez un espace pour la détente et la revitalisation.
                HabitTrack vous permet de suivre votre temps passé à l'extérieur, vous encourageant à maintenir cette connexion essentielle
                avec la nature, qui, à son tour, boostera votre productivité et votre sentiment général de bonheur. Laissez la nature vous
                recharger et vous inspirer au quotidien.
            """,
            'image': 'evasion.jpg'
        },
        'yoga-meditation-pleine-conscience': {
            'titre': 'Yoga et Méditation : Ancrer la Pleine Conscience dans Votre Journée',
            'contenu': """
                Dans le tumulte de la vie quotidienne, trouver un équilibre et une paix intérieure est essentiel. Le yoga et la méditation
                offrent des outils puissants pour cultiver la pleine conscience et renforcer la connexion entre le corps et l'esprit.
                Faire du yoga renforce la souplesse, l'équilibre et la force physique, tandis que la méditation calme le mental,
                réduit l'anxiété et améliore la concentration. Ces habitudes, pratiquées régulièrement, peuvent transformer votre
                réponse au stress et augmenter votre résilience. Elles vous aident à rester ancré dans le moment présent et à développer
                une meilleure compréhension de vous-même. Utilisez HabitTrack pour suivre vos sessions de yoga ou de méditation,
                visualisez votre constance et observez comment ces pratiques enrichissent progressivement votre vie, vous apportant
                sérénité et clarté.
            """,
            'image': 'yoga2.jpeg'
        },
    }

    article = articles_simules.get(slug) 

    if not article:
        raise Http404("Cet article de blog n'existe pas.")

    context = {
        'article': article,
        'slug': slug 
    }
    return render(request, 'blog_detail.html', context)
#-----------------------------------------Vue pour le blog--------------------------------------------------
def blog_view(request):
    """
    Vue pour afficher la page du blog.
    """
    return render(request, 'blog.html', {})

#-----------------------------------------Vue pour l'inscription--------------------------------------------------
def inscription(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Vous êtes inscrit(e), Bienvenue !')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/inscription.html', {'form': form})

#-----------------------------------------Vue pour la connnexion----------------------------------------------------
def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Connexion réussie !')
            return redirect('dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'registration/connexion.html')

#-----------------------------------------Vue pour la déconnexion----------------------------------------------------
def deconnexion(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie !')
    return redirect('connexion')

#-----------------------------------------Vue pour ajouter une habitude----------------------------------------------------
@login_required
def ajouter_habitude(request):
    if request.method == 'POST':
        form = HabitudeForm(request.POST)
        if form.is_valid():
            habitude_instance = form.save(commit=False)
            habitude_instance.utilisateur = request.user
            habitude_instance.save()
            messages.success(request, f"L'habitude '{habitude_instance.titre}' a été ajoutée avec succès !")
            return redirect('dashboard')
    else:
        form = HabitudeForm()
    return render(request, 'ajouter_habitude.html', {'form': form})

#-----------------------------------------Vue pour le dashboard----------------------------------------------------
@login_required
def dashboard(request):
    user_habitudes = Habitude.objects.filter(utilisateur=request.user).order_by('-date_creation')

    all_stats = {}
    aujourd_hui = timezone.now().date()

   
    all_user_suivis_count = Suivi.objects.filter(habitude__utilisateur=request.user, fait=True).count()

   
    if user_habitudes.count() >= 1 and not Badge.objects.filter(utilisateur=request.user, nom_badge='Débutant').exists():
        Badge.objects.create(utilisateur=request.user, nom_badge='Débutant', description_badge='Vous avez créé votre première habitude.')
        messages.success(request, "Félicitations ! Vous avez gagné le badge 'Débutant' !")

   
    if all_user_suivis_count >= 7 and not Badge.objects.filter(utilisateur=request.user, nom_badge='Assidu').exists():
        Badge.objects.create(utilisateur=request.user, nom_badge='Assidu', description_badge='Vous avez marqué 7 habitudes comme faites au total.')
        messages.success(request, "Super ! Vous avez gagné le badge 'Assidu' !")

    # Badge: Champion (Marquer 30 habitudes comme faites au total)
    if all_user_suivis_count >= 30 and not Badge.objects.filter(utilisateur=request.user, nom_badge='Champion').exists():
        Badge.objects.create(utilisateur=request.user, nom_badge='Champion', description_badge='Vous avez marqué 30 habitudes comme faites au total.')
        messages.success(request, "Incroyable ! Vous avez gagné le badge 'Champion' !")

    # Récupérer tous les badges gagnés par l'utilisateur courant
    earned_badges = Badge.objects.filter(utilisateur=request.user).order_by('date_obtention')


    for habitude in user_habitudes:
        # --- Données pour le graphique (7 derniers jours) ---
        donnees_graphique = []
        jours_graphique = []
        for i in range(7):
            current_day_for_chart = aujourd_hui - timedelta(days=6 - i)
            jours_graphique.append(current_day_for_chart.strftime('%a'))
            # Vérifie si au moins un suivi fait existe pour ce jour
            fait_ce_jour = Suivi.objects.filter(habitude=habitude, date=current_day_for_chart, fait=True).exists()
            donnees_graphique.append(1 if fait_ce_jour else 0)

        # --- Calcul des jours consécutifs réussis ---
        consecutive_days = 0
        current_day_consecutive = aujourd_hui
        while True:
            # S'arrête si on dépasse la date de création de l'habitude
            if current_day_consecutive < habitude.date_creation:
                break

            # Vérifie si l'habitude a été marquée comme "faite" pour ce jour
            suivi_fait_ce_jour = Suivi.objects.filter(
                habitude=habitude,
                date=current_day_consecutive,
                fait=True
            ).exists()

            if suivi_fait_ce_jour:
                consecutive_days += 1
                current_day_consecutive -= timedelta(days=1) # Passe au jour précédent
            else:
                # Si l'habitude n'a pas été faite, la séquence est brisée
                break

        all_stats[str(habitude.id)] = {
            'titre': habitude.titre,
            'jours': jours_graphique,
            'donnees': donnees_graphique,
            'consecutive_days': consecutive_days,
        }

    context = {
        'habitudes': user_habitudes,
        'stats': all_stats,
        'earned_badges': earned_badges, # Passer les badges gagnés au template
    }
    return render(request, 'dashboard.html', context)

#-----------------------------------------Vue pour modifier l'habitude----------------------------------------------------
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
        form = HabitudeForm(instance=habitude)
    return render(request, 'modifier_habitude.html', {'form': form})

#-----------------------------------------Vue pour supprimer l'habitude----------------------------------------------------
@login_required
def supprimer_habitude(request, id):
    habitude = get_object_or_404(Habitude, pk=id, utilisateur=request.user)
    titre_habitude = habitude.titre
    habitude.delete()
    messages.info(request, f"L'habitude '{titre_habitude}' a été supprimée.")
    return redirect('dashboard')

#-----------------------------------------Vue pour marquer une habitude comme faite----------------------------------------------------
@login_required
def marquer_habitude(request, id):
    habitude = get_object_or_404(Habitude, pk=id, utilisateur=request.user)
    today = date.today()

    suivi, created = Suivi.objects.get_or_create(
        habitude=habitude,
        date=today, # Utiliser 'date' comme nom de champ, comme défini dans models.py
        defaults={'fait': True}
    )

    if not created:
        if not suivi.fait:
            suivi.fait = True
            suivi.save()
            messages.success(request, f"L'habitude '{habitude.titre}' a été marquée comme faite pour aujourd'hui !")
        else:
            messages.info(request, f"L'habitude '{habitude.titre}' est déjà marquée comme faite pour aujourd'hui.")
    else:
        messages.success(request, f"L'habitude '{habitude.titre}' a été marquée comme faite pour aujourd'hui !")

    
    habitude.derniere_realisation = today
    habitude.save()

    return redirect('dashboard')
