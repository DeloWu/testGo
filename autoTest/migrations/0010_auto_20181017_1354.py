# Generated by Django 2.0.1 on 2018-10-17 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('autoTest', '0009_auto_20181017_1103'),
    ]

    operations = [
        migrations.AddField(
            model_name='api',
            name='content_type',
            field=models.CharField(default='json', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='report',
            name='testCases',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='autoTest.TestCases'),
        ),
        migrations.AlterField(
            model_name='testcases',
            name='setup_hooks',
            field=models.CharField(blank=True, default='[]', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='testcases',
            name='teardown_hooks',
            field=models.CharField(blank=True, default='[]', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='teststep',
            name='setup_hooks',
            field=models.CharField(blank=True, default='[]', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='teststep',
            name='teardown_hooks',
            field=models.CharField(blank=True, default='[]', max_length=200, null=True),
        ),
    ]
