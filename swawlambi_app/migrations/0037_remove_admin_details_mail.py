# Generated by Django 5.1.4 on 2025-04-06 05:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swawlambi_app', '0036_admin_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin_details',
            name='mail',
        ),
    ]
