# Generated by Django 5.2.3 on 2025-07-02 21:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cafes', '0001_initial'),
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='globalcustomerdb',
            name='cafe_slug',
        ),
        migrations.RemoveField(
            model_name='globalcustomerdb',
            name='city',
        ),
        migrations.AlterField(
            model_name='cafecustomerdb',
            name='cafe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cafedb', to='cafes.cafe'),
        ),
    ]
