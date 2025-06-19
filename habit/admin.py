from django.contrib import admin
from .models import Habitude, Suivi, Badge

# Register your models here.
admin.site.register(Habitude)
admin.site.register(Suivi)
admin.site.register(Badge)