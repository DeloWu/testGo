# Generated by Django 2.0.1 on 2018-09-26 02:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autoTest', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='prj_id',
            new_name='pro_id',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='prj_name',
            new_name='pro_name',
        ),
    ]
