import os
from django.db import models
from datetime import date

# Create your models here.

class Ingredient(models.Model):
    class Meta:
        db_table = 'ingredient'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=300)
    unit = models.CharField(max_length=100)
    unitary_price = models.FloatField()
    kcalories = models.FloatField()
    icon_name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class RecipeCategory(models.Model):
    class Meta:
        db_table = 'recipe_category'

    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50)


class Recipe(models.Model):
    class Meta:
        db_table = 'recipe'

    recipe_categories = (
        (1, 'Arroces'),
        (2, 'Bocadillos y Hamburguesas'),
        (3, 'Carnes'),
        (4, 'Ensaladas y Bowls'),
        (5, 'Guisos'),
        (6, 'Legumbres'),
        (7, 'Pastas'),
        (8, 'Pescado y marisco'),
        (9, 'Salteado'),
        (10, 'Sandwich'),
        (11, 'Sopas y crema'),
        (12, 'Verduras y vegetales'),
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=5000)
    category = models.ForeignKey(RecipeCategory, on_delete=models.SET_DEFAULT, default=12)
    steps = models.CharField(max_length=5000)
    cooking_time = models.IntegerField()
    is_lunch = models.BooleanField(default=True)
    image_path = models.ImageField(upload_to = date.today().strftime("%%Y/%m/%d"), blank=True)
    total_stars = models.FloatField(default=0.0)
    num_scores = models.PositiveBigIntegerField(default=0)
    user = models.BigIntegerField()
    servings = models.BigIntegerField()
    ingredients = models.ManyToManyField(Ingredient, through='Compound')

    def __str__(self):
        return self.name


class Compound(models.Model):
    class Meta:
        unique_together = (('recipe', 'ingredient'),)
        db_table = 'compound'
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.SET_NULL, null=True)
    quantity = models.FloatField()

    def __str__(self):
        return "Ingredient: " + self.ingredient.name + " Recipe: " + self.recipe.name

class Add(models.Model):
    class Meta:
        unique_together = (('user', 'ingredient'),)
        db_table = 'add'
    user = models.BigIntegerField()
    ingredient = models.ForeignKey(Ingredient, on_delete=models.SET_NULL, null=True)
    quantity = models.FloatField()

    def __str__(self):
        return "User: " + self.user.email + " Ingredient: " + self.ingredient.name

class Schedule(models.Model):
    class Meta:
        # unique_together = (('user', 'date', 'is_lunch'),)
        db_table = 'schedule'

    user = models.BigIntegerField()
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField()
    is_lunch = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Score(models.Model):
    class Meta:
        unique_together = (('user', 'recipe'),)
        db_table = 'score'

    user = models.BigIntegerField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    num_stars = models.FloatField(default=0.0)

    def __str__(self):
        return self.name