# Generated by Django 4.1 on 2022-12-10 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_schedule_mid_dept'),
    ]

    operations = [
        migrations.AddField(
            model_name='terminal',
            name='tcode',
            field=models.CharField(default=None, max_length=3, null=True, unique=True),
        ),
    ]
