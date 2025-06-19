# habit/forms.py

from django import forms
from .models import Habitude

# Formulaire pour la création et la modification d'une habitude
class HabitudeForm(forms.ModelForm):
    class Meta:
        # Spécifie le modèle sur lequel ce formulaire est basé
        model = Habitude
        # Inclut tous les champs nécessaires, y compris 'description_habit'
        fields = ['titre', 'description_habit', 'frequence']
        # Ajoute des labels et des widgets Bootstrap pour un meilleur rendu visuel
        labels = {
            'titre': 'Nom de l\'habitude',
            'description_habit': 'Description de l\'habitude', # Nouveau label pour ce champ
            'frequence': 'Fréquence',
        }
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Boire 2L d\'eau'}),
            'description_habit': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Décrivez votre habitude en quelques mots...', 'rows': 3}), # Widget pour zone de texte
            'frequence': forms.Select(attrs={'class': 'form-select'}),
        }