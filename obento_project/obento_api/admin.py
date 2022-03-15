from django.contrib import admin
from .models import Compound, Ingredient, Recipe

# Register your models here.

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Compound)
