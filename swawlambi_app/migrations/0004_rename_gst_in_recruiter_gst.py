# Generated by Django 5.1.4 on 2024-12-10 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swawlambi_app', '0003_alter_student_profile_summary'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recruiter',
            old_name='gst_in',
            new_name='gst',
        ),
    ]
