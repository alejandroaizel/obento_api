from unicodedata import decimal
from django.db import models

# Create your models here.


class Hero(models.Model):
    name = models.CharField(max_length=60)
    alias = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    # recipe_categories = (
    #     (1, 'Arroces'),
    #     (2, 'Bocadillos y Hamburguesas'),
    #     (3, 'Carnes'),
    #     (4, 'Ensaladas y Bowls'),
    #     (5, 'Guisos'),
    #     (6, 'Legumbres'),
    #     (7, 'Pastas'),
    #     (8, 'Pescado y marisco'),
    #     (9, 'Salteado'),
    #     (10, 'Sandwich'),
    #     (11, 'Sopas y crema'),
    #     (12, 'Verduras y vegetales'),
    # )
    id = models.AutoField(primary_key=True)
    # userId = models.ForeignKey()
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=5000)
    category = models.IntegerField()
    steps = models.CharField(max_length=5000)
    estimated_cost = models.DecimalField(decimal_places=2, max_digits=8)
    is_launch = models.BooleanField(default=True)
    image_path = models.CharField(max_length=300)
    total_stars = models.PositiveBigIntegerField(default=0)
    num_scores = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=300)
    unit = models.CharField(max_length=100)
    unitary_price = models.FloatField()
    kcalories = models.FloatField()
    icon_name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Compound(models.Model):
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient_id = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()

    def __str__(self):
        return self.name
