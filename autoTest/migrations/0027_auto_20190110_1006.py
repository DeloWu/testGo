# Generated by Django 2.0.1 on 2019-01-10 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autoTest', '0026_auto_20181224_1026'),
    ]

    operations = [
        migrations.CreateModel(
            name='MockServer',
            fields=[
                ('mockServer_id', models.AutoField(primary_key=True, serialize=False)),
                ('mockServer_name', models.CharField(max_length=20)),
                ('uri', models.CharField(max_length=200)),
                ('relative_pro', models.CharField(max_length=10)),
                ('relative_api', models.CharField(max_length=10)),
                ('setup_hooks', models.CharField(blank=True, default='[]', max_length=200)),
                ('teardown_hooks', models.CharField(blank=True, default='[]', max_length=200)),
                ('expect_status_code', models.IntegerField(default=200)),
                ('expect_headers', models.TextField(blank=True, default='')),
                ('expect_response_content_type', models.CharField(blank=True, default='json', max_length=10)),
                ('expect_response', models.TextField(blank=True, default='')),
                ('status', models.CharField(blank=True, default='1', max_length=2)),
                ('conditions', models.TextField(blank=True, default='')),
                ('description', models.CharField(blank=True, default='', max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='api',
            name='default_mockServer_id',
            field=models.CharField(blank=True, default='', max_length=4),
        ),
        migrations.AddField(
            model_name='api',
            name='mock_status',
            field=models.CharField(blank=True, default='False', max_length=10),
        ),
    ]