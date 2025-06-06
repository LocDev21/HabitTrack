from django.db import models
from django.contrib.auth.models import User

# Create your models here.
#------------------------------Table Habitude------------------------------------

class Habitude (models.Model):
    titre = models.TextField()
    description_habit = models.TextField(blank=True)
    frequence_choix = (
        ('quotidien','Quotidien'),
        ('hebdomadaire','Hebdomadaire')
    )
    frequence = models.CharField(max_length=25,choices=frequence_choix)
    date_creation = models.DateField(auto_now_add=True)
    utilisateur = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.titre 
    
#------------------------------Table Suivi---------------------------------------

class Suivi (models.Model):
    habitude = models.ForeignKey(Habitude,on_delete=models.CASCADE) 
    date = models.DateField()
    fait = models.BooleanField(default=False)

    def __str__(self):
        statut = 'Fait' if self.fait==True else 'Non Fait'
        return f"{self.habitude.titre} - {self.date} : {statut}"
    
#------------------------------Table Badge---------------------------------------

class Badge (models.Model):
    nom_badge = models.CharField(max_length=50)
    description_badge = models.TextField(blank=True)
    date_obtention = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom_badge} obtenu : {self.date_obtention}"