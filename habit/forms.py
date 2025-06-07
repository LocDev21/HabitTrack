from django import forms 
from .models import Habitude

class HabitudeForm (forms.ModelForm):
    class Meta:
        model=Habitude
        fields = ['titre', 'description_habit', 'frequence']