# Generated by Django 4.0.3 on 2022-03-20 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obento_api', '0002_schedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='servings',
            field=models.BigIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='user',
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
    ]
