# Generated by Django 4.1 on 2022-10-29 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_alter_tickets_issuedby'),
    ]

    operations = [
        migrations.AddField(
            model_name='tickets',
            name='voucher',
            field=models.CharField(default=None, max_length=100, null=True, unique=True),
        ),
    ]