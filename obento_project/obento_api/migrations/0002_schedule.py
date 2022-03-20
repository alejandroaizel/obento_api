# Generated by Django 4.0.3 on 2022-03-20 11:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('obento_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.BigIntegerField()),
                ('date', models.DateTimeField()),
                ('is_lunch', models.BooleanField(default=True)),
                ('recipe', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='obento_api.recipe')),
            ],
            options={
                'db_table': 'schedule',
                'unique_together': {('user', 'recipe', 'date', 'is_lunch')},
            },
        ),
    ]
