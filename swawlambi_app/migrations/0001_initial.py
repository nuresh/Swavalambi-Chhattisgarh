# Generated by Django 5.1.4 on 2024-12-10 12:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_super_admin', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department_name', models.CharField(max_length=100)),
                ('head_of_department', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Recruiter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('address', models.TextField()),
                ('gst_in', models.CharField(max_length=15)),
                ('industry_name', models.CharField(max_length=40)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('course_name', models.CharField(help_text='For example - B.Tech', max_length=100)),
                ('branch_name', models.CharField(max_length=100)),
                ('semester', models.IntegerField(default=1, help_text='For example - 1')),
                ('enrollment_number', models.CharField(max_length=30)),
                ('roll_number', models.CharField(max_length=30)),
                ('gender', models.CharField(max_length=30)),
                ('date_of_birth', models.DateField(null=True)),
                ('course_starting_year', models.IntegerField(help_text='For example - 2019')),
                ('course_ending_year', models.IntegerField(help_text='For example - 2023')),
                ('profile_tagline', models.CharField(blank=True, help_text="Example - 'Java Developer' ", max_length=1000)),
                ('profile_summary', models.TextField(blank=True, help_text="Example - 'I am a Java Developer, I have 2 years of experience' ")),
                ('experience', models.IntegerField(help_text='For example - 2')),
                ('skills', models.CharField(help_text='Please add comma separated skills, For example - C++,Python,Java,AWS ', max_length=1000)),
                ('resume', models.CharField(help_text='Please provide a viewable link to your resume by uploading it to google drive/github ', max_length=1000)),
                ('linkedin', models.CharField(blank=True, max_length=1000)),
                ('github', models.CharField(blank=True, max_length=1000)),
                ('website', models.CharField(blank=True, max_length=1000)),
                ('email_address', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(help_text='Please enter 10 digits only', max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
