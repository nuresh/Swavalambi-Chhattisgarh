# Generated by Django 5.1.4 on 2025-01-21 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swawlambi_app', '0010_job_applications'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='phone_number',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='recruiter',
            name='phone_number',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
