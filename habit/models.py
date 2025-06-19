from django.db import models
from django.contrib.auth.models import User
from datetime import date # Importe date pour le champ derniere_realisation

# Modèle pour définir une habitude
class Habitude(models.Model):
    # L'utilisateur à qui appartient cette habitude (relation un-à-plusieurs)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    # Le titre ou le nom de l'habitude (type Texte)
    titre = models.TextField()
    # Description de l'habitude (optionnelle)
    description_habit = models.TextField(blank=True)

    # Choix pour la fréquence de l'habitude
    FREQUENCE_CHOIX = [
        ('quotidien', 'Quotidien'),
        ('hebdomadaire', 'Hebdomadaire')
    ]
    # Fréquence de l'habitude (choix parmi 'quotidien' ou 'hebdomadaire')
    frequence = models.CharField(max_length=25, choices=FREQUENCE_CHOIX)
    # Date de création de l'habitude (automatiquement définie à la création)
    date_creation = models.DateField(auto_now_add=True)
    # Champ pour stocker la dernière date de réalisation de l'habitude.
    # Il est utile pour l'affichage dans le tableau de bord et peut être nul initialement.
    derniere_realisation = models.DateField(null=True, blank=True)
    
    # Nouveau champ pour le suivi hebdomadaire: indique si l'habitude doit être cochée par défaut chaque semaine
    # Utile pour les habitudes qui ne sont pas faites 'chaque jour' mais 'au moins une fois par semaine'
    # Ce champ n'est pas directement utilisé pour l'image, mais pour la modulabilité du suivi
    suivi_par_defaut = models.BooleanField(default=False, help_text="Marquer comme 'fait' automatiquement si aucune action n'est prise pour la période.")


    def __str__(self):
        # Représentation en chaîne de caractères de l'objet Habitude
        return f"{self.titre} ({self.utilisateur.username})"

# Modèle pour suivre la réalisation quotidienne des habitudes
class Suivi(models.Model):
    # L'habitude associée à ce suivi
    habitude = models.ForeignKey(Habitude, on_delete=models.CASCADE)
    # La date à laquelle l'habitude a été suivie
    date = models.DateField()
    # Booléen indiquant si l'habitude a été faite ou non ce jour-là
    fait = models.BooleanField(default=False)

    class Meta:
        # Contrainte pour s'assurer qu'il n'y a qu'un seul suivi par habitude et par jour
        unique_together = ('habitude', 'date')

    def __str__(self):
        # Représentation en chaîne de caractères de l'objet Suivi
        statut = 'Fait' if self.fait else 'Non Fait'
        return f"{self.habitude.titre} - {self.date} : {statut}"

# Modèle pour les badges (récompenses)
class Badge(models.Model):
    # L'utilisateur qui a obtenu ce badge
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE) 
    # Nom du badge
    nom_badge = models.CharField(max_length=50)
    # Description du badge (optionnelle)
    description_badge = models.TextField(blank=True)
    # Date d'obtention du badge (automatiquement définie à la création)
    date_obtention = models.DateField(auto_now_add=True)
    
    # Nouveau champ pour le type de badge visuel (ex: 'tree', 'star', etc.)
    type_visuel = models.CharField(max_length=50, blank=True, null=True, 
                                   help_text="Type de représentation visuelle (ex: 'tree', 'star')")
    # Chemin vers l'image si le badge a une représentation visuelle spécifique
    image_url = models.CharField(max_length=255, blank=True, null=True,
                                 help_text="Chemin vers l'image du badge si applicable")

    def __str__(self):
        # Représentation en chaîne de caractères de l'objet Badge
        return f"{self.nom_badge} (par {self.utilisateur.username})"