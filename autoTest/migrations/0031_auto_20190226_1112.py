# Generated by Django 2.0.1 on 2019-02-26 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autoTest', '0030_auto_20190226_0858'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Encryption',
        ),
        migrations.RenameField(
            model_name='function',
            old_name='func_id',
            new_name='function_id',
        ),
        migrations.RemoveField(
            model_name='function',
            name='func_name',
        ),
        migrations.AddField(
            model_name='function',
            name='function_name',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='function',
            name='description',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
