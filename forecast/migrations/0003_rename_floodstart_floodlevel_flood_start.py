# Generated by Django 3.2.7 on 2021-09-16 08:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0002_alter_floodpronearea_radius'),
    ]

    operations = [
        migrations.RenameField(
            model_name='floodlevel',
            old_name='floodstart',
            new_name='flood_start',
        ),
    ]
