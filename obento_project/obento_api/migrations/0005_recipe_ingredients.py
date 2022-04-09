# Generated by Django 4.0.3 on 2022-04-08 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obento_api', '0004_alter_recipe_total_stars_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='obento_api.Compound', to='obento_api.ingredient'),
        ),
    ]
