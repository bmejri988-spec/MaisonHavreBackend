from django.contrib import admin

from .models import ChaletModel, Option, Terrain

admin.site.register((ChaletModel, Terrain, Option))
