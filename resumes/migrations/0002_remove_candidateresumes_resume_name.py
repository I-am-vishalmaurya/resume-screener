# Generated by Django 2.2.27 on 2022-02-14 15:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidateresumes',
            name='resume_name',
        ),
    ]
