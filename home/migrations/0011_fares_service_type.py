# Generated by Django 4.1 on 2022-12-11 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_alter_fares_route'),
    ]

    operations = [
        migrations.AddField(
            model_name='fares',
            name='service_type',
            field=models.CharField(default='economy', max_length=100),
        ),
    ]
