# habit/forms.py

from django import forms
from .models import Habitude
from django.contrib.auth.forms import PasswordChangeForm # Importe le formulaire de changement de mot de passe de Django

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

# Nouveau formulaire personnalisé pour le changement de mot de passe
class PasswordChangeCustomForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajoute les classes Bootstrap aux champs du formulaire
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            # Supprime le help_text par défaut si vous ne le voulez pas
            field.help_text = None

