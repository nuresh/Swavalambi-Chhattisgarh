# Generated by Django 5.1.4 on 2025-01-21 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swawlambi_app', '0012_alter_student_github_alter_student_linkedin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='phone_number',
            field=models.CharField(default=123456789, max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recruiter',
            name='phone_number',
            field=models.CharField(default='abc', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='student',
            name='phone_number',
            field=models.IntegerField(default=3, max_length=10),
            preserve_default=False,
        ),
    ]
