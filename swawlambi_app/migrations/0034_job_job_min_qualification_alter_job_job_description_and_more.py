# Generated by Django 5.1.4 on 2025-03-31 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swawlambi_app', '0033_alter_department_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='job_min_qualification',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_experience',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_location',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_salary',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_skills',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
