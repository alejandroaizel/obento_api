from django.contrib import admin
from .models import Compound, Hero, Ingredient, Recipe

# Register your models here.

admin.site.register(Hero)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Compound)