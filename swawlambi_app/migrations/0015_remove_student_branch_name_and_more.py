# Generated by Django 5.1.4 on 2025-01-21 04:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swawlambi_app', '0014_alter_department_phone_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='branch_name',
        ),
        migrations.RemoveField(
            model_name='student',
            name='course_name',
        ),
    ]
