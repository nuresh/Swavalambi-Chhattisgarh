# Generated by Django 5.1.4 on 2025-03-15 04:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swawlambi_app', '0023_rename_phone_number_recruiter_company_phone_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recruiter',
            name='industry_name',
        ),
    ]
